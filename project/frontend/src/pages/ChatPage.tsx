import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  TextField,
  Button,
  IconButton,
  CircularProgress,
  Divider,
  alpha,
} from '@mui/material';
import {
  Send as SendIcon,
  Add as AddIcon,
  ChatBubbleOutline as ChatIcon,
} from '@mui/icons-material';
import { chatAPI } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
}

const ChatPage = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const response = await chatAPI.getAllConversations();
      if (response.data.success && response.data.data?.conversation_ids) {
        const convs = response.data.data.conversation_ids.map((id: string) => ({
          id,
          title: id.slice(0, 8), // 使用 ID 的前 8 位作为标题
        }));
        setConversations(convs);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleSelectConversation = async (conversation: Conversation) => {
    try {
      setSelectedConversation(conversation);
      setCurrentConversationId(conversation.id);
      const response = await chatAPI.getConversation(conversation.id);
      if (response.data.success && response.data.data?.memories) {
        const msgs = response.data.data.memories.map((mem: any) => ({
          role: mem.role === 'user' ? 'user' : 'assistant',
          content: mem.content,
          timestamp: new Date(),
        }));
        setMessages(msgs);
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isSending) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsSending(true);

    // 如果没有当前对话ID，注册新对话
    if (!currentConversationId) {
      try {
        const registerResponse = await chatAPI.registerConversation();
        if (registerResponse.data.success && registerResponse.data.data?.conversation_id) {
          // 设置当前对话ID
          setCurrentConversationId(registerResponse.data.data.conversation_id);
          // 重新加载对话列表
          await loadConversations();
        }
      } catch (error) {
        console.error('Failed to register conversation:', error);
      }
    }

    try {
      console.log('Sending message:', userMessage.content);
      const response = await chatAPI.sendMessage(userMessage.content);
      console.log('Full response:', response);
      console.log('Response data:', response.data);
      console.log('Response success:', response.data.success);
      console.log('Response data.data:', response.data.data);
      
      if (response.data.success && response.data.data) {
        console.log('Response content:', response.data.data.response);
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.data.response || '没有收到响应',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        console.log('Response not successful or no data');
        const errorMessage = response.data.data?.error || response.data.message || '请求失败，请稍后重试';
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: errorMessage,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error: any) {
      console.error('Failed to send message:', error);
      console.error('Error response:', error.response);
      console.error('Error message:', error.message);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `错误: ${error.message || '请求失败，请稍后重试'}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = () => {
    setSelectedConversation(null);
    setCurrentConversationId(null);
    setMessages([]);
  };

  return (
    <Box
      sx={{
        height: 'calc(100vh - 64px)',
        backgroundColor: 'background.default',
        display: 'flex',
      }}
    >
      {/* 左侧对话列表 */}
      <Box
        sx={{
          width: 280,
          backgroundColor: 'background.paper',
          borderRight: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box
          sx={{
            px: 3,
            py: 2,
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ChatIcon sx={{ fontSize: 24, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              对话列表
            </Typography>
          </Box>
          <IconButton
            onClick={handleNewChat}
            sx={{
              color: 'text.primary',
              '&:hover': {
                backgroundColor: alpha('#3b82f6', 0.1),
              },
            }}
          >
            <AddIcon />
          </IconButton>
        </Box>
        <List sx={{ flex: 1, overflow: 'auto', py: 1 }}>
          {isLoadingConversations ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          ) : conversations.length === 0 ? (
            <Box sx={{ px: 3, py: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                暂无对话
              </Typography>
            </Box>
          ) : (
            conversations.map((conv) => (
              <ListItem key={conv.id} disablePadding>
                <ListItemButton
                  selected={selectedConversation?.id === conv.id}
                  onClick={() => handleSelectConversation(conv)}
                  sx={{
                    mx: 1,
                    borderRadius: 2,
                    mb: 0.5,
                    backgroundColor: selectedConversation?.id === conv.id
                      ? alpha('#3b82f6', 0.1)
                      : 'transparent',
                    '&:hover': {
                      backgroundColor: selectedConversation?.id === conv.id
                        ? alpha('#3b82f6', 0.15)
                        : alpha('#3b82f6', 0.05),
                    },
                  }}
                >
                  <ListItemText
                    primary={conv.title}
                    primaryTypographyProps={{
                      fontSize: '0.9rem',
                      fontWeight: selectedConversation?.id === conv.id ? 600 : 400,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))
          )}
        </List>
      </Box>

      {/* 右侧对话区域 */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Chat Header */}
        <Box
          sx={{
            px: 3,
            py: 2,
            backgroundColor: 'background.paper',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {selectedConversation ? `对话 ${selectedConversation.title}` : '新对话'}
          </Typography>
        </Box>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          px: 3,
          py: 2,
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'text.secondary',
            }}
          >
            <ChatIcon sx={{ fontSize: 80, mb: 3, opacity: 0.5 }} />
            <Typography variant="h5" gutterBottom>
              {selectedConversation ? '加载对话中...' : '开始新的对话'}
            </Typography>
            <Typography variant="body2">
              {selectedConversation ? '请稍候' : '输入您的问题，AI助手将为您提供帮助'}
            </Typography>
          </Box>
        ) : (
          <Box sx={{ maxWidth: 900, mx: 'auto' }}>
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2,
                }}
              >
                <Box
                  sx={{
                    maxWidth: '70%',
                    backgroundColor:
                      msg.role === 'user'
                        ? 'primary.main'
                        : alpha('#1e293b', 0.8),
                    color: msg.role === 'user' ? 'white' : 'text.primary',
                    px: 2.5,
                    py: 1.5,
                    borderRadius: 2,
                    wordBreak: 'break-word',
                  }}
                >
                  <Typography variant="body1">{msg.content}</Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      mt: 1,
                      display: 'block',
                      opacity: 0.7,
                      fontSize: '0.75rem',
                    }}
                  >
                    {msg.timestamp.toLocaleTimeString()}
                  </Typography>
                </Box>
              </Box>
            ))}
            {isSending && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                <Box
                  sx={{
                    backgroundColor: alpha('#1e293b', 0.8),
                    px: 2.5,
                    py: 1.5,
                    borderRadius: 2,
                  }}
                >
                  <CircularProgress size={20} />
                </Box>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
        )}
      </Box>

      {/* Input Area */}
      <Box
        sx={{
          px: 3,
          py: 2,
          backgroundColor: 'background.paper',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Box sx={{ maxWidth: 900, mx: 'auto', display: 'flex', gap: 1.5 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题..."
            disabled={isSending}
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                backgroundColor: alpha('#1e293b', 0.5),
              },
            }}
          />
          <IconButton
            color="primary"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isSending}
            sx={{
              alignSelf: 'flex-end',
              backgroundColor: 'primary.main',
              color: 'white',
              '&:hover': {
                backgroundColor: 'primary.dark',
              },
              '&:disabled': {
                backgroundColor: 'action.disabledBackground',
              },
              width: 48,
              height: 48,
            }}
          >
            {isSending ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
          </IconButton>
        </Box>
      </Box>
      </Box>
    </Box>
  );
};

export default ChatPage;
