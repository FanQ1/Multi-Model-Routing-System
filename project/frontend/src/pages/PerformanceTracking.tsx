
import React, { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { performanceAPI, modelRegistryAPI } from '../services/api'

interface Model {
  id: string
  name: string
}

interface PerformanceRecord {
  model_id: string
  period: string
  avg_latency_ms: number
  success_rate: number
  uptime_percentage: number
  violations: number
}

const PerformanceTracking = () => {
  const [models, setModels] = useState<Model[]>([])
  const [records, setRecords] = useState<PerformanceRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [selectedModel, setSelectedModel] = useState('')
  const [formData, setFormData] = useState({
    model_id: '',
    period: new Date().toISOString().slice(0, 10),
    avg_latency_ms: 1000,
    success_rate: 99,
    uptime_percentage: 99.9,
    violations: 0
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

  const fetchRecords = async (modelId: string) => {
    try {
      const response = await performanceAPI.getModelPerformance(modelId)
      if (response.data.success) {
        setRecords(response.data.data.records || [])
        setSelectedModel(modelId)
      } else {
        console.error('Failed to fetch performance records:', response.data.message)
      }
    } catch (error) {
      console.error('Failed to fetch performance records:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await performanceAPI.reportPerformance(formData)
      if (response.data.success) {
        setOpen(false)
        if (selectedModel) {
          fetchRecords(selectedModel)
        }
      } else {
        console.error('Failed to report performance:', response.data.message)
      }
    } catch (error) {
      console.error('Failed to report performance:', error)
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Performance Tracking</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Report Performance
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Model
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Model</InputLabel>
                <Select
                  value={selectedModel}
                  label="Model"
                  onChange={(e) => fetchRecords(e.target.value)}
                  disabled={loading}
                >
                  {models.map((model) => (
                    <MenuItem key={model.id} value={model.id}>
                      {model.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Records
              </Typography>
              {selectedModel ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Period</TableCell>
                        <TableCell>Avg Latency</TableCell>
                        <TableCell>Success Rate</TableCell>
                        <TableCell>Uptime</TableCell>
                        <TableCell>Violations</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {records.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} align="center">
                            No performance records for this model
                          </TableCell>
                        </TableRow>
                      ) : (
                        records.map((record, index) => (
                          <TableRow key={index}>
                            <TableCell>{record.period}</TableCell>
                            <TableCell>
                              {record.avg_latency_ms}ms
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={`${record.success_rate}%`}
                                color={record.success_rate >= 99 ? 'success' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>{record.uptime_percentage}%</TableCell>
                            <TableCell>
                              <Chip
                                label={record.violations}
                                color={record.violations === 0 ? 'success' : 'error'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="textSecondary">
                  Select a model to view performance records
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Report Performance</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Model</InputLabel>
                  <Select
                    value={formData.model_id}
                    label="Model"
                    onChange={(e) => setFormData({ ...formData, model_id: e.target.value })}
                  >
                    {models.map((model) => (
                      <MenuItem key={model.id} value={model.id}>
                        {model.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Period"
                  type="date"
                  value={formData.period}
                  onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                  InputLabelProps={{ shrink: true }}
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
                  label="Success Rate (%)"
                  type="number"
                  value={formData.success_rate}
                  onChange={(e) => setFormData({ ...formData, success_rate: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Uptime (%)"
                  type="number"
                  step="0.1"
                  value={formData.uptime_percentage}
                  onChange={(e) => setFormData({ ...formData, uptime_percentage: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Violations"
                  type="number"
                  value={formData.violations}
                  onChange={(e) => setFormData({ ...formData, violations: parseInt(e.target.value) })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Submit Report</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default PerformanceTracking
