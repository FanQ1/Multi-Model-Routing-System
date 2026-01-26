
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
  const [result, setResult] = useState<RoutingResult | null>(null)
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

    setLoading(true)
    try {
      const response = await routingAPI.routeQuery(query, capability || undefined)
      console.log('Full response:', response)
      console.log('Response data:', response.data)
      // 正确处理后端返回的响应数据
      if (response.data && response.data.success) {
        console.log('Setting result with data:', response.data.data)
        setResult(response.data.data)
      } else {
        console.log('Setting result with full data:', response.data)
        setResult(response.data)
      }
      fetchStats() // Refresh stats after routing
    } catch (error) {
      console.error('Failed to route query:', error)
    } finally {
      setLoading(false)
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

              {result && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Routing Result
                  </Typography>
                  {/* 调试信息 */}
                  <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
                    Debug: {JSON.stringify(result, null, 2)}
                  </Typography>
                  {result.model_name && (
                    <Box>
                      <Typography variant="body1">
                        <strong>Model:</strong> {result.model_name}
                      </Typography>
                    </Box>
                  )}
                  {result.response && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Typography variant="body2" gutterBottom>
                        <strong>Model Response:</strong>
                      </Typography>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {result.response}
                      </Typography>
                    </Box>
                  )}
                  {result.success === false && (
                    <Box>
                      <Typography color="error">{result.error}</Typography>
                      {result.suggestion && (
                        <Typography variant="body2" color="textSecondary">
                          {result.suggestion}
                        </Typography>
                      )}
                    </Box>
                  )}
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
