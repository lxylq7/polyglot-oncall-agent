package org.example.client;


import org.example.config.RestTemplateConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import javax.swing.text.html.parser.Entity;
import javax.xml.ws.Response;
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

    public Map<String,Object> agentChat(String sessionId, String question
    , List<Map<String,Object>> history) {
        String url = aiServiceUrl + "/api/agent/chat";
        //构建请求要发送的数据 请求体
        Map<String,Object> body = new HashMap<>();
        body.put("session_id",sessionId);
        body.put("question", question);
        body.put("history", history);
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

    public Map<String,Object> addDocument(String content,String fileName) {
        String url = aiServiceUrl + "/api/rag/add_document";
        //构建请求要发送的数据 请求体
        Map<String,Object> metadata = new HashMap<>();
        metadata.put("file_name",fileName);
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
