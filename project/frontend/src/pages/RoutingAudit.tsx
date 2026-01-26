
import React, { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip
} from '@mui/material'
import { Send as SendIcon } from '@mui/icons-material'
import { routingAPI } from '../services/api'

interface RoutingStats {
  total_requests: number
  unique_models: number
  top_models: Array<{ model: string; requests: number }>
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  model_name?: string
}

interface RoutingResult {
  success: boolean
  model_id?: string
  model_name?: string
  trust_score?: number
  reason?: string
  blockchain_tx?: string
  estimated_latency?: number
  cost_per_1k?: number
  error?: string
  suggestion?: string
  response?: string
}

const RoutingAudit = () => {
  const [stats, setStats] = useState<RoutingStats | null>(null)
  const [query, setQuery] = useState('')
  const [capability, setCapability] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await routingAPI.getStats(24)
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch routing stats:', error)
    }
  }

  const handleRoute = async () => {
    if (!query.trim()) return

    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content: query
    }
    setMessages(prev => [...prev, userMessage])
    
    setLoading(true)
    try {
      const response = await routingAPI.routeQuery(query, capability || undefined)
      // 正确处理后端返回的响应数据
      if (response.data && response.data.success) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.data.response || '',
          model_name: response.data.data.model_name
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        const errorMessage: Message = {
          role: 'assistant',
          content: response.data?.error || '请求失败'
        }
        setMessages(prev => [...prev, errorMessage])
      }
      fetchStats() // Refresh stats after routing
    } catch (error) {
      console.error('Failed to route query:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: '请求失败，请重试'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      setQuery('')
    }
  }

  const handleCommitBatch = async () => {
    const period = new Date().toISOString().slice(0, 16).replace('T', '-')
    try {
      await routingAPI.commitBatch(period)
      fetchStats()
    } catch (error) {
      console.error('Failed to commit batch:', error)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Routing Audit Trail
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Test and monitor routing decisions with full blockchain transparency
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Routing
              </Typography>
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="User Query"
                  multiline
                  rows={3}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter a query to route..."
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="Required Capability (optional)"
                  value={capability}
                  onChange={(e) => setCapability(e.target.value)}
                  placeholder="e.g., coding, writing, math"
                />
              </Box>
              <Button
                variant="contained"
                startIcon={<SendIcon />}
                onClick={handleRoute}
                disabled={loading}
                fullWidth
              >
                {loading ? 'Routing...' : 'Route Query'}
              </Button>

              {/* 对话历史 */}
              {messages.length > 0 && (
                <Box sx={{ mt: 3, maxHeight: '400px', overflow: 'auto' }}>
                  {messages.map((msg, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      {msg.role === 'user' ? (
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                          <Paper sx={{ p: 2, bgcolor: 'primary.main', color: 'white', maxWidth: '70%' }}>
                            <Typography variant="body1">{msg.content}</Typography>
                          </Paper>
                        </Box>
                      ) : (
                        <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                          <Paper sx={{ p: 2, bgcolor: '#2d3748', color: 'white', maxWidth: '70%' }}>
                            {msg.model_name && (
                              <Typography variant="caption" color="rgba(255,255,255,0.7)" sx={{ display: 'block', mb: 1 }}>
                                模型: {msg.model_name}
                              </Typography>
                            )}
                            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                              {msg.content}
                            </Typography>
                          </Paper>
                        </Box>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Routing Statistics (Last 24 Hours)
              </Typography>
              {stats && (
                <Box>
                  <Typography variant="body1">
                    <strong>Total Requests:</strong> {stats.total_requests}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Unique Models:</strong> {stats.unique_models}
                  </Typography>
                  <Button
                    variant="outlined"
                    onClick={handleCommitBatch}
                    sx={{ mt: 2 }}
                    fullWidth
                  >
                    Commit Batch to Blockchain
                  </Button>
                </Box>
              )}

              {stats?.top_models && stats.top_models.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Top Models
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Model</TableCell>
                          <TableCell align="right">Requests</TableCell>
                          <TableCell align="right">Share</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {stats.top_models.map((model, index) => (
                          <TableRow key={index}>
                            <TableCell>{model.model}</TableCell>
                            <TableCell align="right">{model.requests}</TableCell>
                            <TableCell align="right">
                              {((model.requests / stats.total_requests) * 100).toFixed(1)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default RoutingAudit
