package org.example.client;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 打通java -> python 控制链
 */
@Component
public class AiServiceClient {

    @Autowired
    private RestTemplate restTemplate;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    public Map<String, Object> agentChat(String sessionId, String question
            , List<Map<String, String>> history) {
        String url = aiServiceUrl + "/api/agent/chat";
        //构建请求要发送的数据 请求体
        Map<String, Object> body = new HashMap<>();
        body.put("session_id", sessionId);
        body.put("question", question);
        body.put("history", history);
        //设置请求头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        //把请求头和请求体打包
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);
        //发送post请求
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>() {
                }  //把返回的JSON自动转成Map<String,Object>

        );
        return response.getBody();
    }

    public void agentChatStream(String sessionId, String question
            , List<Map<String, String>> history
            , java.util.function.Consumer<String> onChunk) { //回调 每收到内容就触发
        String url = aiServiceUrl + "/api/agent/chat_stream";
        //构建请求要发送的数据 请求体
        Map<String, Object> body = new HashMap<>();
        body.put("session_id", sessionId);
        body.put("question", question);
        body.put("history", history);
        restTemplate.execute(
                url,
                HttpMethod.POST,
                request -> {
                    // 错误的 execute 是最底层方法 需要自己手工写
                    request.getHeaders().setContentType(MediaType.APPLICATION_JSON);
                    String json = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(body);
                    request.getBody().write(json.getBytes(StandardCharsets.UTF_8));
                },
                responseExtractor -> { //接受并解析流式返回
                    try (BufferedReader reader = new BufferedReader(
                            new InputStreamReader(
                                    responseExtractor.getBody(),
                                    StandardCharsets.UTF_8
                            )
                    )) {
                        String line;
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data:")) {
                                String data = line.substring(5).trim();
                                if (!data.isEmpty() && !"[DONE]".equals(data)) {
                                    onChunk.accept(data);
                                }
                            }
                        }
                    }
                    return null;
                }
        );
    }

    public Map<String,Object> addDocument(String content,String fileName) {
        String url = aiServiceUrl + "/api/rag/add_document";
        //构建请求要发送的数据 请求体
        Map<String,Object> metadata = new HashMap<>();
        metadata.put("filename",fileName);
        Map<String,Object> body = new HashMap<>();
        body.put("content",content);
        body.put("metadata",metadata);
        //设置请求头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        //把请求头和请求体打包
        HttpEntity<Map<String,Object>> entity = new HttpEntity<>(body,headers);
        //发送post请求
        ResponseEntity<Map<String,Object>> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>(){}  //把返回的JSON自动转成Map<String,Object>
        );
        return response.getBody();
    }
}
