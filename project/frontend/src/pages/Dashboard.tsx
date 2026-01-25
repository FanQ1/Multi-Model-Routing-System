
import React, { useEffect, useState } from 'react'
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  Card, 
  CardContent,
  LinearProgress
} from '@mui/material'
import { 
  Storage as ModelsIcon,
  Verified as VerifiedIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material'
import { dashboardAPI } from '../services/api'

interface DashboardData {
  total_models: number
  verified_models: number
  total_violations: number
  recent_performance: any[]
  top_models: any[]
}

const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardAPI.getOverview()
        setData(response.data)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return <LinearProgress />
  }

  if (!data) {
    return (
      <Box p={3}>
        <Typography color="error">Failed to load dashboard data</Typography>
      </Box>
    )
  }

  const StatCard = ({ title, value, icon, color }: any) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        ModelChain Dashboard
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Real-time overview of the AI model trust layer
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Models"
            value={data.total_models}
            icon={<ModelsIcon fontSize="large" />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Verified Models"
            value={data.verified_models}
            icon={<VerifiedIcon fontSize="large" />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Violations"
            value={data.total_violations}
            icon={<WarningIcon fontSize="large" />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Trust Score"
            value={data.top_models.length > 0 
              ? (data.top_models.reduce((acc, m) => acc + m.trust_score, 0) / data.top_models.length).toFixed(1)
              : 'N/A'
            }
            icon={<TrendingUpIcon fontSize="large" />}
            color="#ed6c02"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Models by Trust Score
            </Typography>
            {data.top_models.map((model, index) => (
              <Box key={model.model_id} sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body1">
                    {index + 1}. {model.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Score: {model.trust_score.toFixed(1)}/100
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={model.trust_score} 
                  sx={{ mt: 1 }}
                />
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Performance Reports
            </Typography>
            {data.recent_performance.length > 0 ? (
              data.recent_performance.map((report, index) => (
                <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                  <Typography variant="body1">
                    Model: {report.model_id}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Period: {report.period}
                  </Typography>
                  <Box display="flex" justifyContent="space-between" mt={1}>
                    <Typography variant="body2">
                      Latency: {report.avg_latency_ms}ms
                    </Typography>
                    <Typography variant="body2">
                      Success Rate: {report.success_rate}%
                    </Typography>
                  </Box>
                </Box>
              ))
            ) : (
              <Typography color="textSecondary">No performance reports yet</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
