package org.example.service;

import org.example.entity.ChatMemory;
import org.example.repository.ChatMemoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class MemoryService {

    @Autowired
    private ChatMemoryRepository chatMemoryRepository;

    /**
     * 根据用户id 查询最近20条记录 返回给AI当上下文
     */
    public List<Map<String,String>> recallAsHistory(String sessionId) {
        //数据库查出来最新 -> 最旧
        List<ChatMemory> rows = chatMemoryRepository.findTop20BySessionIdOrderByCreatedAtDesc(sessionId);
        //ai要从最近的开始看 所以反转
        Collections.reverse(rows);
        //准备返回给ai的格式
        List<Map<String,String>> history = new ArrayList<>();
        for (ChatMemory row : rows) {
            //只保留用户说的和ai回答的
            if (!"user".equals(row.getRole()) && !"assistant".equals(row.getRole())) {
                continue;
            }
            Map<String,String> msg = new HashMap<>();
            msg.put("role",row.getRole());
            msg.put("content",row.getContent());
            history.add(msg);
        }
        return history;
    }

    /**
     * 保存一轮问答
     */
    public void saveTurn(String sessionId,String question,String answer){
        ChatMemory u = new ChatMemory();
        u.setSessionId(sessionId);
        u.setRole("user");
        u.setContent(question);
        chatMemoryRepository.save(u);

        ChatMemory a = new ChatMemory();
        a.setSessionId(sessionId);
        a.setRole("assistant");
        a.setContent(answer);
        chatMemoryRepository.save(a);
    }
}
