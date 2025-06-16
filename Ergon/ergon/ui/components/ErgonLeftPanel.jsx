import React, { useState } from 'react';
import { 
  Box, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  ListItemButton,
  Divider,
  Typography
} from '@mui/material';

// Import icons
import GridViewIcon from '@mui/icons-material/GridView';
import ChatIcon from '@mui/icons-material/Chat';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import MemoryIcon from '@mui/icons-material/Memory';
import GitHubIcon from '@mui/icons-material/GitHub';
import EmailIcon from '@mui/icons-material/Email';
import LanguageIcon from '@mui/icons-material/Language';
import SettingsIcon from '@mui/icons-material/Settings';
import FolderIcon from '@mui/icons-material/Folder';
import DashboardIcon from '@mui/icons-material/Dashboard';

/**
 * Left Panel component for Ergon
 * Controls navigation between different Ergon windows
 */
const ErgonLeftPanel = ({ onViewChange, currentView }) => {
  // Define available views
  const views = [
    { id: 'dashboard', name: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'agents', name: 'Agents', icon: <GridViewIcon /> },
    { id: 'chat', name: 'Chat', icon: <ChatIcon /> },
    { id: 'documents', name: 'Documents', icon: <FolderIcon /> },
    { id: 'settings', name: 'Settings', icon: <SettingsIcon /> }
  ];
  
  // Define agent types
  const agentTypes = [
    { id: 'standard', name: 'Standard Agents', icon: <AutoAwesomeIcon /> },
    { id: 'nexus', name: 'Memory Agents', icon: <MemoryIcon /> },
    { id: 'github', name: 'GitHub Agents', icon: <GitHubIcon /> },
    { id: 'mail', name: 'Email Agents', icon: <EmailIcon /> },
    { id: 'browser', name: 'Browser Agents', icon: <LanguageIcon /> }
  ];
  
  return (
    <Box sx={{ width: '100%', height: '100%', overflow: 'auto' }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          NAVIGATION
        </Typography>
      </Box>
      
      <List component="nav" dense>
        {views.map((view) => (
          <ListItem key={view.id} disablePadding>
            <ListItemButton
              selected={currentView === view.id}
              onClick={() => onViewChange(view.id)}
              sx={{
                borderLeft: currentView === view.id 
                  ? '3px solid #2196f3' 
                  : '3px solid transparent',
                '&.Mui-selected': {
                  backgroundColor: 'rgba(33, 150, 243, 0.08)'
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {view.icon}
              </ListItemIcon>
              <ListItemText primary={view.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ my: 1 }} />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          AGENT TYPES
        </Typography>
      </Box>
      
      <List component="nav" dense>
        {agentTypes.map((type) => (
          <ListItem key={type.id} disablePadding>
            <ListItemButton onClick={() => onViewChange('agents', { filter: type.id })}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                {type.icon}
              </ListItemIcon>
              <ListItemText primary={type.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ my: 1 }} />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          RECENT AGENTS
        </Typography>
      </Box>
      
      <List component="nav" dense>
        {['Nexus Assistant', 'GitHub Helper', 'Email Manager'].map((name, i) => (
          <ListItem key={i} disablePadding>
            <ListItemButton onClick={() => onViewChange('chat', { agent: name })}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                {i === 0 ? <MemoryIcon color="primary" /> : 
                 i === 1 ? <GitHubIcon color="primary" /> : 
                 <EmailIcon color="primary" />}
              </ListItemIcon>
              <ListItemText primary={name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default ErgonLeftPanel;