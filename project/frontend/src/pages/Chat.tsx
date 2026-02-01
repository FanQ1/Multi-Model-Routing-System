
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  IconButton,
  CircularProgress,
  Fab,
  Chip
} from '@mui/material';
import {
  Send as SendIcon,
  Add as AddIcon,
  ChatBubbleOutline as ChatIcon
} from '@mui/icons-material';
import { chatAPI } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  messages: Message[];
  createdAt: Date;
}

const Chat = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 加载所有对话
  useEffect(() => {
    loadConversations();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [selectedConversation?.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.getAllConversations();
      if (response.data.success && response.data.data.conversation_ids) {
        const convs = await Promise.all(
          response.data.data.conversation_ids.map(async (id: string) => {
            const convResponse = await chatAPI.getConversation(id);
            if (convResponse.data.success && convResponse.data.data.memories) {
              return {
                id,
                messages: convResponse.data.data.memories.map((msg: any) => ({
                  role: msg.role,
                  content: msg.content,
                  timestamp: new Date(msg.timestamp)
                })),
                createdAt: new Date() // 这里可以根据实际情况调整
              };
            }
            return null;
          })
        );
        setConversations(convs.filter((c): c is Conversation => c !== null));
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await chatAPI.registerConversation();
      if (response.data.success) {
        await loadConversations();
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isSending) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    // 更新本地消息
    if (selectedConversation) {
      const updatedConv = {
        ...selectedConversation,
        messages: [...selectedConversation.messages, userMessage]
      };
      setSelectedConversation(updatedConv);
      setConversations(convs => 
        convs.map(c => c.id === selectedConversation.id ? updatedConv : c)
      );
    }

    setInputMessage('');
    setIsSending(true);

    try {
      const response = await chatAPI.sendMessage(userMessage.content);
      if (response.data.success && response.data.data) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.data.response,
          timestamp: new Date()
        };

        if (selectedConversation) {
          const updatedConv = {
            ...selectedConversation,
            messages: [...selectedConversation.messages, userMessage, assistantMessage]
          };
          setSelectedConversation(updatedConv);
          setConversations(convs => 
            convs.map(c => c.id === selectedConversation.id ? updatedConv : c)
          );
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
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

  return (
    <Container maxWidth="xl" sx={{ height: 'calc(100vh - 120px)', mt: 2 }}>
      <Paper elevation={3} sx={{ height: '100%', display: 'flex', overflow: 'hidden' }}>
        {/* 左侧对话列表 */}
        <Box
          sx={{
            width: '300px',
            borderRight: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ChatIcon />
              对话列表
            </Typography>
          </Box>
          <List sx={{ flex: 1, overflow: 'auto', p: 1 }}>
            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              conversations.map((conv) => (
                <ListItem key={conv.id} disablePadding>
                  <ListItemButton
                    selected={selectedConversation?.id === conv.id}
                    onClick={() => setSelectedConversation(conv)}
                    sx={{ borderRadius: 1, mb: 0.5 }}
                  >
                    <ListItemText
                      primary={`对话 ${conv.id.slice(0, 8)}`}
                      secondary={`${conv.messages.length} 条消息`}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            )}
          </List>
          <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={createNewConversation}
            >
              新建对话
            </Button>
          </Box>
        </Box>

        {/* 右侧对话区域 */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {selectedConversation ? (
            <>
              {/* 对话头部 */}
              <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                <Typography variant="h6">
                  对话 {selectedConversation.id.slice(0, 8)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedConversation.messages.length} 条消息
                </Typography>
              </Box>

              {/* 消息列表 */}
              <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
                {selectedConversation.messages.map((msg, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      mb: 2
                    }}
                  >
                    <Box
                      sx={{
                        maxWidth: '70%',
                        bgcolor: msg.role === 'user' ? 'primary.main' : 'grey.200',
                        color: msg.role === 'user' ? 'white' : 'text.primary',
                        p: 2,
                        borderRadius: 2,
                        wordBreak: 'break-word'
                      }}
                    >
                      <Typography variant="body1">{msg.content}</Typography>
                      <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.7 }}>
                        {msg.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </Box>
                ))}
                {isSending && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                    <Box
                      sx={{
                        bgcolor: 'grey.200',
                        p: 2,
                        borderRadius: 2
                      }}
                    >
                      <CircularProgress size={20} />
                    </Box>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* 输入区域 */}
              <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={4}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="输入消息..."
                    disabled={isSending}
                    variant="outlined"
                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                  />
                  <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isSending}
                    sx={{ alignSelf: 'flex-end' }}
                  >
                    <SendIcon />
                  </IconButton>
                </Box>
              </Box>
            </>
          ) : (
            <Box
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'text.secondary'
              }}
            >
              <ChatIcon sx={{ fontSize: 80, mb: 2 }} />
              <Typography variant="h6">选择或创建一个对话开始聊天</Typography>
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default Chat;
