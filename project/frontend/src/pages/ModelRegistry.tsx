
import React, { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
  IconButton
} from '@mui/material'
import { Add as AddIcon, CheckCircle as VerifiedIcon } from '@mui/icons-material'
import { modelRegistryAPI } from '../services/api'

interface Model {
  id: string
  name: string
  capability_ranks: {
    math: number
    code: number
    if_rank: number
    expert: number
    safety: number
  }
  capability_vector: number[]
  max_tokens: number
  avg_latency_ms: number
  cost_per_1k_usd: number
  stake_eth: number
  is_verified: boolean
  trust_score: number
  registration_time: string
  violations: number
}

const ModelRegistry = () => {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    capability_ranks: {
      math: 1,
      code: 1,
      if_rank: 1,
      expert: 1,
      safety: 1
    },
    max_tokens: 8192,
    avg_latency_ms: 1000,
    cost_per_1k_usd: 0.01,
    stake_eth: 10
  })

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await modelRegistryAPI.getModels()
      if (response.data.success) {
        setModels(response.data.data)
      } else {
        console.error('Failed to fetch models:', response.data.message)
      }
    } catch (error) {
      console.error('Failed to fetch models:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await modelRegistryAPI.registerModel({
        ...formData
      })
      if (response.data.success) {
        setOpen(false)
        fetchModels()
      } else {
        console.error('Failed to register model:', response.data.message)
      }
    } catch (error) {
      console.error('Failed to register model:', error)
    }
  }

  const handleVerify = async (modelId: string) => {
    try {
      const response = await modelRegistryAPI.verifyModel(modelId)
      if (response.data.success) {
        fetchModels()
      } else {
        console.error('Failed to verify model:', response.data.message)
      }
    } catch (error) {
      console.error('Failed to verify model:', error)
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Model Registry</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Register New Model
        </Button>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Model Name</TableCell>
                <TableCell>Capability Ranks</TableCell>
                <TableCell>Max Tokens</TableCell>
                <TableCell>Avg Latency</TableCell>
                <TableCell>Cost/1K</TableCell>
                <TableCell>Stake (ETH)</TableCell>
                <TableCell>Trust Score</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : models.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    No models registered yet
                  </TableCell>
                </TableRow>
              ) : (
                models.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell>{model.name}</TableCell>
                    <TableCell>
                      <Box sx={{ fontSize: '0.875rem' }}>
                        Math: {model.capability_ranks?.math ?? 'N/A'}<br />
                        Code: {model.capability_ranks?.code ?? 'N/A'}<br />
                        IF: {model.capability_ranks?.if_rank ?? 'N/A'}<br />
                        Expert: {model.capability_ranks?.expert ?? 'N/A'}<br />
                        Safety: {model.capability_ranks?.safety ?? 'N/A'}
                      </Box>
                    </TableCell>
                    <TableCell>{model.max_tokens ? model.max_tokens.toLocaleString() : 'N/A'}</TableCell>
                    <TableCell>{model.avg_latency_ms ? `${model.avg_latency_ms}ms` : 'N/A'}</TableCell>
                    <TableCell>{model.cost_per_1k_usd ? `$${model.cost_per_1k_usd.toFixed(4)}` : 'N/A'}</TableCell>
                    <TableCell>{model.stake_eth ? model.stake_eth.toFixed(2) : 'N/A'}</TableCell>
                    <TableCell>{model.trust_score ? `${model.trust_score.toFixed(1)}/100` : 'N/A'}</TableCell>
                    <TableCell>
                      {model.is_verified ? (
                        <Chip 
                          icon={<VerifiedIcon />} 
                          label="Verified" 
                          color="success" 
                          size="small"
                        />
                      ) : (
                        <Chip label="Pending" color="warning" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {!model.is_verified && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleVerify(model.id)}
                        >
                          Verify
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Register New Model</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Model Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Math Rank"
                  type="number"
                  value={formData.capability_ranks.math}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    capability_ranks: { ...formData.capability_ranks, math: parseInt(e.target.value) } 
                  })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Code Rank"
                  type="number"
                  value={formData.capability_ranks.code}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    capability_ranks: { ...formData.capability_ranks, code: parseInt(e.target.value) } 
                  })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="IF Rank"
                  type="number"
                  value={formData.capability_ranks.if_rank}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    capability_ranks: { ...formData.capability_ranks, if_rank: parseInt(e.target.value) } 
                  })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Expert Rank"
                  type="number"
                  value={formData.capability_ranks.expert}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    capability_ranks: { ...formData.capability_ranks, expert: parseInt(e.target.value) } 
                  })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Safety Rank"
                  type="number"
                  value={formData.capability_ranks.safety}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    capability_ranks: { ...formData.capability_ranks, safety: parseInt(e.target.value) } 
                  })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Max Tokens"
                  type="number"
                  value={formData.max_tokens}
                  onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Avg Latency (ms)"
                  type="number"
                  value={formData.avg_latency_ms}
                  onChange={(e) => setFormData({ ...formData, avg_latency_ms: parseInt(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Cost per 1K Tokens (USD)"
                  type="number"
                  inputProps={{
                    step: "0.0001"
                  }}
                  value={formData.cost_per_1k_usd}
                  onChange={(e) => setFormData({ ...formData, cost_per_1k_usd: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Stake (ETH)"
                  type="number"
                  inputProps={{
                    step: "0.1"
                  }}
                  value={formData.stake_eth}
                  onChange={(e) => setFormData({ ...formData, stake_eth: parseFloat(e.target.value) })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Register</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default ModelRegistry
