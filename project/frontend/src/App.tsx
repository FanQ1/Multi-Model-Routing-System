
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Container, Box } from '@mui/material'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import ModelRegistry from './pages/ModelRegistry'
import RoutingAudit from './pages/RoutingAudit'
import PerformanceTracking from './pages/PerformanceTracking'
import TrustScores from './pages/TrustScores'

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/models" element={<ModelRegistry />} />
          <Route path="/routing" element={<RoutingAudit />} />
          <Route path="/performance" element={<PerformanceTracking />} />
          <Route path="/trust" element={<TrustScores />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App
