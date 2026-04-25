package org.example.repository;

import org.example.entity.ChatMemory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChatMemoryRepository extends JpaRepository<ChatMemory,Long> {

    List<ChatMemory> findTop20BySessionIdOrderByCreatedAtDesc(String sessionId);

    long countBySessionId(String sessionId);

}
