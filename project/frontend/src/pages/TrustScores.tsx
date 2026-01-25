
import React, { useEffect, useState } from 'react'
import {
  Box,
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
  Typography,
  Chip,
  LinearProgress
} from '@mui/material'
import { trustScoreAPI } from '../services/api'

interface TrustScore {
  model_id: string
  model_name: string
  trust_score: number
  is_verified: boolean
  violations: number
}

const TrustScores = () => {
  const [scores, setScores] = useState<TrustScore[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchScores()
  }, [])

  const fetchScores = async () => {
    try {
      const response = await trustScoreAPI.getAllScores()
      setScores(response.data)
    } catch (error) {
      console.error('Failed to fetch trust scores:', error)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#2e7d32' // green
    if (score >= 60) return '#ed6c02' // orange
    return '#d32f2f' // red
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Poor'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Trust Scores
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Dynamic reputation system based on model performance and reliability
      </Typography>

      <Grid container spacing={3}>
        {loading ? (
          <Grid item xs={12}>
            <Typography align="center">Loading...</Typography>
          </Grid>
        ) : scores.length === 0 ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography align="center">No trust scores available yet</Typography>
            </Paper>
          </Grid>
        ) : (
          scores.map((score) => (
            <Grid item xs={12} md={6} lg={4} key={score.model_id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">{score.model_name}</Typography>
                    {score.is_verified && (
                      <Chip label="Verified" color="success" size="small" />
                    )}
                  </Box>

                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Trust Score
                    </Typography>
                    <Box display="flex" alignItems="center" mb={1}>
                      <Typography variant="h4" sx={{ mr: 2, color: getScoreColor(score.trust_score) }}>
                        {score.trust_score.toFixed(1)}
                      </Typography>
                      <Chip
                        label={getScoreLabel(score.trust_score)}
                        sx={{
                          backgroundColor: getScoreColor(score.trust_score),
                          color: 'white'
                        }}
                      />
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={score.trust_score}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getScoreColor(score.trust_score)
                        }
                      }}
                    />
                  </Box>

                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">
                      Violations: {score.violations}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Status: {score.is_verified ? 'Active' : 'Pending'}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {!loading && scores.length > 0 && (
        <Paper sx={{ mt: 3 }}>
          <Box p={2}>
            <Typography variant="h6" gutterBottom>
              Trust Score Breakdown
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Model</TableCell>
                    <TableCell>Score</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Violations</TableCell>
                    <TableCell>Performance</TableCell>
                    <TableCell>Reliability</TableCell>
                    <TableCell>Usage</TableCell>
                    <TableCell>Age</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {scores.map((score) => (
                    <TableRow key={score.model_id}>
                      <TableCell>{score.model_name}</TableCell>
                      <TableCell>
                        <Typography sx={{ color: getScoreColor(score.trust_score) }}>
                          {score.trust_score.toFixed(1)}/100
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={score.is_verified ? 'Verified' : 'Pending'}
                          color={score.is_verified ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{score.violations}</TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={score.trust_score * 0.4}
                          sx={{ width: 100 }}
                        />
                      </TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={score.trust_score * 0.3}
                          sx={{ width: 100 }}
                        />
                      </TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={score.trust_score * 0.2}
                          sx={{ width: 100 }}
                        />
                      </TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={score.trust_score * 0.1}
                          sx={{ width: 100 }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </Paper>
      )}
    </Box>
  )
}

export default TrustScores
