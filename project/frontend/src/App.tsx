
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import Sidebar from './components/Sidebar'
import Models from './pages/Models'
import ChatPage from './pages/ChatPage'
import More from './pages/More'

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Routes>
          <Route path="/" element={<Navigate to="/models" replace />} />
          <Route path="/models" element={<Models />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/more" element={<More />} />
        </Routes>
      </Box>
    </Box>
  )
}

export default App
