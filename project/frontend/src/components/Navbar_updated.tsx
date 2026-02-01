
import React from 'react'
import { NavLink } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Storage as ModelsIcon,
  Route as RoutingIcon,
  Assessment as PerformanceIcon,
  TrendingUp as TrustIcon,
  ChatBubbleOutline as ChatIcon
} from '@mui/icons-material'

const Navbar = () => {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { path: '/models', label: 'Model Registry', icon: <ModelsIcon /> },
    { path: '/routing', label: 'Routing Audit', icon: <RoutingIcon /> },
    { path: '/performance', label: 'Performance', icon: <PerformanceIcon /> },
    { path: '/trust', label: 'Trust Scores', icon: <TrustIcon /> },
    { path: '/chat', label: 'Chat', icon: <ChatIcon /> }
  ]

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ModelChain - AI Model Trust Layer
        </Typography>
        <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              component={NavLink}
              to={item.path}
              sx={{ mx: 1 }}
              style={({ isActive }) => ({
                backgroundColor: isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
              })}
              startIcon={item.icon}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
