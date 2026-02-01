import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ModelTraining as ModelIcon,
  Chat as ChatIcon,
  MoreHoriz as MoreIcon,
  ChevronLeft as ChevronLeftIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const DRAWER_WIDTH = 280;

const menuItems = [
  { text: '模型管理', icon: <ModelIcon />, path: '/models' },
  { text: '智能对话', icon: <ChatIcon />, path: '/chat' },
  { text: '更多功能', icon: <MoreIcon />, path: '/more', disabled: true },
];

const Sidebar = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const drawer = (
    <Box>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 3,
          py: 2,
        }}
      >
        <Typography variant="h6" component="div" sx={{ fontWeight: 700, color: 'primary.main' }}>
          AI Platform
        </Typography>
        {isMobile && (
          <IconButton onClick={handleDrawerToggle} sx={{ color: 'text.primary' }}>
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />
      <List sx={{ px: 2, py: 3 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
            <ListItemButton
              onClick={() => !item.disabled && handleNavigation(item.path)}
              disabled={item.disabled}
              sx={{
                borderRadius: 2,
                py: 1.5,
                px: 2,
                backgroundColor: location.pathname === item.path ? 'primary.main' : 'transparent',
                color: location.pathname === item.path ? 'white' : 'text.primary',
                '&:hover': {
                  backgroundColor: location.pathname === item.path ? 'primary.dark' : 'rgba(59, 130, 246, 0.1)',
                },
                '&.Mui-disabled': {
                  opacity: 0.5,
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontWeight: location.pathname === item.path ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
    >
      {/* Mobile */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
            backgroundColor: 'background.paper',
            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        {drawer}
      </Drawer>
      {/* Desktop */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
            backgroundColor: 'background.paper',
            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;
