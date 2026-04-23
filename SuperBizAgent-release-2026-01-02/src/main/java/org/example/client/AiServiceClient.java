package org.example.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;

@Component
public class AiServiceClient {

    private final WebClient webClient;

    public AiServiceClient(@Value("${ai.service.url:http://localhost:8000}") String aiServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(aiServiceUrl)
                .build();
    }

    public Map<String, Object> agentChat(String sessionId, String question, List<Map<String, String>> history) {
        Map<String, Object> requestBody = Map.of(
                "session_id", sessionId,
                "question", question,
                "history", history != null ? history : List.of()
        );

        return webClient.post()
                .uri("/api/agent/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .block();
    }

    public Map<String, Object> ragQuery(String question, List<Map<String, String>> history) {
        Map<String, Object> requestBody = Map.of(
                "question", question,
                "history", history != null ? history : List.of()
        );

        return webClient.post()
                .uri("/api/rag/query")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .block();
    }

    public Map<String, Object> addDocument(String content, String filename) {
        Map<String, Object> requestBody = Map.of(
                "content", content,
                "metadata", Map.of("filename", filename)
        );

        return webClient.post()
                .uri("/api/rag/add_document")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .block();
    }

    public Map<String, Object> healthCheck() {
        return webClient.get()
                .uri("/health")
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .block();
    }
}
