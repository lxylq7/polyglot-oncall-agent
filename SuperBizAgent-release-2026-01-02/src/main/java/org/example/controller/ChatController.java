package org.example.controller;

import lombok.Getter;
import lombok.Setter;
import org.example.client.AiServiceClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.locks.ReentrantLock;

@RestController
@RequestMapping("/api")
public class ChatController {

    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);

    @Autowired
    private AiServiceClient aiServiceClient;

    private final ExecutorService executor = Executors.newCachedThreadPool();

    private final Map<String, SessionInfo> sessions = new ConcurrentHashMap<>();

    private static final int MAX_WINDOW_SIZE = 6;

    private boolean safeSend(SseEmitter emitter, SseMessage message,String scene) {
        try {
            emitter.send(SseEmitter.event() //构建一个sse事件 服务器主动推送时间
                    .name("message") //事件名
                    .data(message, MediaType.APPLICATION_JSON));
            return true;
        } catch (IOException e) {
            logger.error("SSE发送失败 - {}", scene, e);
            emitter.completeWithError(e);
            return false;
        }
    }

    @PostMapping("/chat")
    public ResponseEntity<ApiResponse<ChatResponse>> chat(@RequestBody ChatRequest request) {
        try {
            logger.info("收到对话请求 - SessionId: {}, Question: {}", request.getId(), request.getQuestion());

            if (request.getQuestion() == null || request.getQuestion().trim().isEmpty()) {
                logger.warn("问题内容为空");
                return ResponseEntity.ok(ApiResponse.success(ChatResponse.error("问题内容不能为空")));
            }

            SessionInfo session = getOrCreateSession(request.getId());
            List<Map<String, String>> history = session.getHistory();
            logger.info("会话历史消息对数: {}", history.size() / 2);

            Map<String, Object> result = aiServiceClient.agentChat(
                    request.getId(), request.getQuestion(), history);

            String answer = result != null && result.get("answer") != null
                    ? result.get("answer").toString() : "抱歉，AI 服务暂时不可用";

            session.addMessage(request.getQuestion(), answer);
            logger.info("已更新会话历史 - SessionId: {}, 当前消息对数: {}",
                    request.getId(), session.getMessagePairCount());

            return ResponseEntity.ok(ApiResponse.success(ChatResponse.success(answer)));

        } catch (Exception e) {
            logger.error("对话失败", e);
            return ResponseEntity.ok(ApiResponse.success(ChatResponse.error(e.getMessage())));
        }
    }

    @PostMapping("/chat/clear")
    public ResponseEntity<ApiResponse<String>> clearChatHistory(@RequestBody ClearRequest request) {
        try {
            logger.info("收到清空会话历史请求 - SessionId: {}", request.getId());

            if (request.getId() == null || request.getId().isEmpty()) {
                return ResponseEntity.ok(ApiResponse.error("会话ID不能为空"));
            }

            SessionInfo session = sessions.get(request.getId());
            if (session != null) {
                session.clearHistory();
                return ResponseEntity.ok(ApiResponse.success("会话历史已清空"));
            } else {
                return ResponseEntity.ok(ApiResponse.error("会话不存在"));
            }

        } catch (Exception e) {
            logger.error("清空会话历史失败", e);
            return ResponseEntity.ok(ApiResponse.error(e.getMessage()));
        }
    }

    @PostMapping(value = "/chat_stream", produces = "text/event-stream;charset=UTF-8")
    public SseEmitter chatStream(@RequestBody ChatRequest request) {
        SseEmitter emitter = new SseEmitter(300000L);

        if (request.getQuestion() == null || request.getQuestion().trim().isEmpty()) {
            logger.warn("问题内容为空");
            safeSend(emitter, SseMessage.error("问题内容不能为空"), "chat_stream");
            emitter.complete();
            return emitter;
        }
        executor.execute(() -> { //开启新线程 不阻塞主线程
            try {
                logger.info("收到流式对话请求 - SessionId: {}, Question: {}", request.getId(), request.getQuestion());
                SessionInfo session = getOrCreateSession(request.getId());
                List<Map<String, String>> history = session.getHistory();
                StringBuilder fullAnswer = new StringBuilder();
                aiServiceClient.agentChatStream(
                        request.getId(),
                        request.getQuestion(),
                        history,
                        chunk -> {  //java.util.function.Consumer<String> onChunk的具体实现
                            fullAnswer.append(chunk);
                            if (!safeSend(emitter,SseMessage.content(chunk),"chat_stream")) {
                                return;
                            }
                        }
                );
                session.addMessage(request.getQuestion(), fullAnswer.toString());
                logger.info("已更新会话历史 - SessionId: {}, 当前消息对数: {}",
                        request.getId(), session.getMessagePairCount());
                if (!safeSend(emitter,SseMessage.done(),"chat_stream")) {
                    return;
                }
                emitter.complete();
            } catch (Exception e) {
                logger.error("流式对话失败", e);
                if (!safeSend(emitter,SseMessage.error(e.getMessage()),"chat_stream")) {
                    return;
                }
                emitter.completeWithError(e);
            }
        });
        return emitter;
    }
    private static final String REPORT_SEPARATOR = "\n\n" + new String(new char[60]).replace("\0", "=") + "\n";

    @PostMapping(value = "/ai_ops", produces = "text/event-stream;charset=UTF-8")
    public SseEmitter aiOps() {
        SseEmitter emitter = new SseEmitter(600000L);

        executor.execute(() -> {
            try {
                logger.info("收到 AI 智能运维请求");

                if (!safeSend(emitter,SseMessage.content("正在读取告警并拆解任务...\n"),"chat_stream")) {
                    return;
                }
                StringBuilder reportBuilder = new StringBuilder();

                if (!safeSend(emitter,SseMessage.content(REPORT_SEPARATOR),"chat_stream")) {
                    return;
                }

                if (!safeSend(emitter,SseMessage.content("📋 **告警分析报告**\n\n"),"chat_stream")) {
                    return;
                }

                aiServiceClient.agentChatStream(
                        "aiops",
                        "查询当前活动告警并分析根因",
                        null,
                        chunk -> {
                            if (!safeSend(emitter,SseMessage.content(chunk),"chat_stream")) {
                                return;
                            }
                            reportBuilder.append(chunk);
                        }
                );

                if (!safeSend(emitter,SseMessage.content(REPORT_SEPARATOR),"chat_stream")) {
                    return;
                }
                if (!safeSend(emitter,SseMessage.done(),"chat_stream")) {
                    return;
                }
                emitter.complete();

            } catch (Exception e) {
                logger.error("AI Ops 流程失败", e);
                safeSend(emitter,SseMessage.error("AI Ops 流程失败: " + e.getMessage()),"ai_ops");
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }

    @GetMapping("/chat/session/{sessionId}")
    public ResponseEntity<ApiResponse<SessionInfoResponse>> getSessionInfo(@PathVariable String sessionId) {
        try {
            logger.info("收到获取会话信息请求 - SessionId: {}", sessionId);

            SessionInfo session = sessions.get(sessionId);
            if (session != null) {
                SessionInfoResponse response = new SessionInfoResponse();
                response.setSessionId(sessionId);
                response.setMessagePairCount(session.getMessagePairCount());
                response.setCreateTime(session.createTime);
                return ResponseEntity.ok(ApiResponse.success(response));
            } else {
                return ResponseEntity.ok(ApiResponse.error("会话不存在"));
            }

        } catch (Exception e) {
            logger.error("获取会话信息失败", e);
            return ResponseEntity.ok(ApiResponse.error(e.getMessage()));
        }
    }

    private SessionInfo getOrCreateSession(String sessionId) {
        if (sessionId == null || sessionId.isEmpty()) {
            sessionId = UUID.randomUUID().toString();
        }
        return sessions.computeIfAbsent(sessionId, SessionInfo::new);
    }

    private static class SessionInfo {
        private final String sessionId;
        private final List<Map<String, String>> messageHistory;
        private final long createTime;
        private final ReentrantLock lock;

        public SessionInfo(String sessionId) {
            this.sessionId = sessionId;
            this.messageHistory = new ArrayList<>();
            this.createTime = System.currentTimeMillis();
            this.lock = new ReentrantLock();
        }

        public void addMessage(String userQuestion, String aiAnswer) {
            lock.lock();
            try {
                Map<String, String> userMsg = new HashMap<>();
                userMsg.put("role", "user");
                userMsg.put("content", userQuestion);
                messageHistory.add(userMsg);

                Map<String, String> assistantMsg = new HashMap<>();
                assistantMsg.put("role", "assistant");
                assistantMsg.put("content", aiAnswer);
                messageHistory.add(assistantMsg);

                int maxMessages = MAX_WINDOW_SIZE * 2;
                while (messageHistory.size() > maxMessages) {
                    messageHistory.remove(0);
                    if (!messageHistory.isEmpty()) {
                        messageHistory.remove(0);
                    }
                }
            } finally {
                lock.unlock();
            }
        }

        public List<Map<String, String>> getHistory() {
            lock.lock();
            try {
                return new ArrayList<>(messageHistory);
            } finally {
                lock.unlock();
            }
        }

        public void clearHistory() {
            lock.lock();
            try {
                messageHistory.clear();
                logger.info("会话 {} 历史消息已清空", sessionId);
            } finally {
                lock.unlock();
            }
        }

        public int getMessagePairCount() {
            lock.lock();
            try {
                return messageHistory.size() / 2;
            } finally {
                lock.unlock();
            }
        }
    }

    @Setter
    @Getter
    public static class ChatRequest {
        @com.fasterxml.jackson.annotation.JsonProperty(value = "Id")
        @com.fasterxml.jackson.annotation.JsonAlias({"id", "ID"})
        private String Id;

        @com.fasterxml.jackson.annotation.JsonProperty(value = "Question")
        @com.fasterxml.jackson.annotation.JsonAlias({"question", "QUESTION"})
        private String Question;
    }

    @Setter
    @Getter
    public static class ClearRequest {
        @com.fasterxml.jackson.annotation.JsonProperty(value = "Id")
        @com.fasterxml.jackson.annotation.JsonAlias({"id", "ID"})
        private String Id;
    }

    @Setter
    @Getter
    public static class SessionInfoResponse {
        private String sessionId;
        private int messagePairCount;
        private long createTime;
    }

    @Setter
    @Getter
    public static class ChatResponse {
        private boolean success;
        private String answer;
        private String errorMessage;

        public static ChatResponse success(String answer) {
            ChatResponse response = new ChatResponse();
            response.setSuccess(true);
            response.setAnswer(answer);
            return response;
        }

        public static ChatResponse error(String errorMessage) {
            ChatResponse response = new ChatResponse();
            response.setSuccess(false);
            response.setErrorMessage(errorMessage);
            return response;
        }
    }

    @Setter
    @Getter
    public static class SseMessage {
        private String type;
        private String data;

        public static SseMessage content(String data) {
            SseMessage message = new SseMessage();
            message.setType("content");
            message.setData(data);
            return message;
        }

        public static SseMessage error(String errorMessage) {
            SseMessage message = new SseMessage();
            message.setType("error");
            message.setData(errorMessage);
            return message;
        }

        public static SseMessage done() {
            SseMessage message = new SseMessage();
            message.setType("done");
            message.setData(null);
            return message;
        }
    }

    @Getter
    @Setter
    public static class ApiResponse<T> {
        private int code;
        private String message;
        private T data;

        public static <T> ApiResponse<T> success(T data) {
            ApiResponse<T> response = new ApiResponse<>();
            response.setCode(200);
            response.setMessage("success");
            response.setData(data);
            return response;
        }

        public static <T> ApiResponse<T> error(String message) {
            ApiResponse<T> response = new ApiResponse<>();
            response.setCode(500);
            response.setMessage(message);
            return response;
        }
    }
}
