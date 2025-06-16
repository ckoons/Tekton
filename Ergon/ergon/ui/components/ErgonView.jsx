import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, Tabs, Tab, Typography, Paper, TextField, Button, IconButton,
  List, ListItem, ListItemText, Chip, Divider, Dialog, DialogTitle,
  DialogContent, DialogActions, FormControl, InputLabel, Select, 
  MenuItem, Switch, FormControlLabel, Grid, CircularProgress, Alert,
  Card, CardContent, CardActions
} from '@mui/material';

// Import icons
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import ChatIcon from '@mui/icons-material/Chat';
import GitHubIcon from '@mui/icons-material/GitHub';
import EmailIcon from '@mui/icons-material/Email';
import MemoryIcon from '@mui/icons-material/Memory';
import LanguageIcon from '@mui/icons-material/Language';
import SendIcon from '@mui/icons-material/Send';
import RefreshIcon from '@mui/icons-material/Refresh';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ImageIcon from '@mui/icons-material/Image';
import TextSnippetIcon from '@mui/icons-material/TextSnippet';
import DescriptionIcon from '@mui/icons-material/Description';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';

// Import API service that wraps CLI functionality
import ErgonApiService from '../services/ApiService';

/**
 * Ergon Component View
 * Provides a React-based GUI for Ergon that wraps CLI functions
 */
const ErgonView = () => {
  // UI state
  const [tabValue, setTabValue] = useState(0);
  const [chatInput, setChatInput] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentDialogOpen, setAgentDialogOpen] = useState(false);
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const [featureRatingMode, setFeatureRatingMode] = useState(false);
  const [planReviewMode, setPlanReviewMode] = useState(false);
  
  // Data state
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your Ergon agent. How can I help you today?' }
  ]);
  
  // Chat session state
  const [chatSession, setChatSession] = useState(null);
  const [thinking, setThinking] = useState(false);
  
  // Form state
  const [newAgentForm, setNewAgentForm] = useState({
    name: '',
    description: '',
    agentType: 'standard',
    model: ''
  });
  
  // Sample data for demo features
  const [features] = useState([
    { id: 1, name: 'Memory Retention', description: 'Ability to remember past conversations', rating: 0 },
    { id: 2, name: 'GitHub Integration', description: 'Ability to work with GitHub repositories', rating: 0 },
    { id: 3, name: 'Email Processing', description: 'Ability to read and compose emails', rating: 0 },
    { id: 4, name: 'Web Browsing', description: 'Ability to browse and extract data from websites', rating: 0 },
    { id: 5, name: 'Plan Generation', description: 'Ability to create implementation plans', rating: 0 }
  ]);
  
  const [samplePlan] = useState({
    title: 'Feature Implementation Plan',
    description: 'Plan for implementing the requested features',
    phases: [
      { 
        name: 'Research Phase', 
        tasks: [
          { name: 'Gather requirements', status: 'completed' },
          { name: 'Research existing solutions', status: 'completed' },
          { name: 'Define acceptance criteria', status: 'in-progress' }
        ]
      },
      { 
        name: 'Development Phase', 
        tasks: [
          { name: 'Create technical design', status: 'not-started' },
          { name: 'Implement core functionality', status: 'not-started' },
          { name: 'Create unit tests', status: 'not-started' }
        ]
      },
      { 
        name: 'Testing Phase', 
        tasks: [
          { name: 'Integration testing', status: 'not-started' },
          { name: 'User acceptance testing', status: 'not-started' }
        ]
      }
    ]
  });
  
  // Refs
  const chatEndRef = useRef(null);
  
  // Load agents on component mount
  useEffect(() => {
    loadAgents();
  }, []);
  
  // Scroll to bottom of chat when messages change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Clean up chat session on unmount
  useEffect(() => {
    return () => {
      if (chatSession) {
        chatSession.endChat();
      }
    };
  }, [chatSession]);
  
  /**
   * Load agents from the API
   */
  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const agentList = await ErgonApiService.getAgents();
      setAgents(agentList);
    } catch (err) {
      setError('Failed to load agents: ' + err.message);
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Select an agent and start chat session if on chat tab
   */
  const handleAgentSelect = async (agent) => {
    setSelectedAgent(agent);
    
    // If we're on the chat tab, initialize chat session
    if (tabValue === 1) {
      startChatSession(agent);
    }
  };
  
  /**
   * Start a new chat session with the selected agent
   */
  const startChatSession = async (agent) => {
    try {
      setLoading(true);
      
      // End existing session if any
      if (chatSession) {
        await chatSession.endChat();
      }
      
      // Reset messages
      setMessages([
        { role: 'assistant', content: `Hello! I'm ${agent.name}, your Ergon agent. How can I help you today?` }
      ]);
      
      // Start new interactive session
      const session = await ErgonApiService.startInteractiveChat(agent.id, {
        onMessage: (message) => {
          setMessages(prev => [...prev, { role: 'assistant', content: message }]);
          setThinking(false);
        },
        onError: (errorMsg) => {
          setError('Agent error: ' + errorMsg);
          setThinking(false);
        },
        onClose: () => {
          setThinking(false);
        },
        disableMemory: !memoryEnabled
      });
      
      setChatSession(session);
    } catch (err) {
      setError('Failed to start chat: ' + err.message);
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Handle sending a message in the chat
   */
  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    // If no agent selected, show a message
    if (!selectedAgent) {
      setMessages(prev => [
        ...prev, 
        { role: 'user', content: chatInput },
        { role: 'assistant', content: 'Please select an agent first.' }
      ]);
      setChatInput('');
      return;
    }
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: chatInput }]);
    
    // Check for special commands
    if (chatInput.startsWith('!plan')) {
      // Set plan review mode
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'I\'ve created an implementation plan. You can review it using the sidebar.' 
        }]);
        setPlanReviewMode(true);
      }, 1000);
    } else if (chatInput.startsWith('!rate')) {
      // Set feature rating mode
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'Let\'s rate the importance of different features for the project.' 
        }]);
        setFeatureRatingMode(true);
      }, 1000);
    } else {
      try {
        // Show thinking state
        setThinking(true);
        
        // Use chat session if available
        if (chatSession) {
          // Message will be added by the onMessage handler
          await chatSession.sendMessage(chatInput);
        } else {
          // For non-interactive mode, use runAgent
          const response = await ErgonApiService.runAgent(
            selectedAgent.id, 
            chatInput, 
            null, 
            'log'
          );
          
          setMessages(prev => [...prev, { role: 'assistant', content: response.message || 'No response' }]);
          setThinking(false);
        }
      } catch (err) {
        setError('Error sending message: ' + err.message);
        setThinking(false);
      }
    }
    
    // Clear input
    setChatInput('');
  };
  
  /**
   * Create a new agent
   */
  const handleCreateAgent = async () => {
    try {
      if (!newAgentForm.name) {
        setError('Agent name is required');
        return;
      }
      
      setLoading(true);
      
      const result = await ErgonApiService.createAgent({
        name: newAgentForm.name,
        description: newAgentForm.description,
        agentType: newAgentForm.agentType,
        model: newAgentForm.model || null
      });
      
      // Reload agents list
      await loadAgents();
      
      // Reset form and close dialog
      setNewAgentForm({
        name: '',
        description: '',
        agentType: 'standard',
        model: ''
      });
      setAgentDialogOpen(false);
      
    } catch (err) {
      setError('Error creating agent: ' + err.message);
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Delete an agent
   */
  const handleDeleteAgent = async (agent) => {
    if (window.confirm(`Are you sure you want to delete agent "${agent.name}"?`)) {
      try {
        setLoading(true);
        await ErgonApiService.deleteAgent(agent.id, true);
        
        // If deleted agent was selected, clear selection
        if (selectedAgent && selectedAgent.id === agent.id) {
          setSelectedAgent(null);
          
          // End chat session if active
          if (chatSession) {
            await chatSession.endChat();
            setChatSession(null);
          }
        }
        
        // Reload agents list
        await loadAgents();
      } catch (err) {
        setError('Error deleting agent: ' + err.message);
      } finally {
        setLoading(false);
      }
    }
  };
  
  /**
   * Rate a feature's importance
   */
  const rateFeature = (featureId, rating) => {
    const updatedFeatures = features.map(feature => 
      feature.id === featureId ? { ...feature, rating } : feature
    );
    setFeatures(updatedFeatures);
  };
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Tab Navigation */}
      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
        <Tab label="Agents" />
        <Tab label="Chat" />
        <Tab label="Documents" />
        <Tab label="Settings" />
      </Tabs>
      
      {/* Error display */}
      {error && (
        <Alert 
          severity="error" 
          onClose={() => setError(null)} 
          sx={{ m: 2 }}
        >
          {error}
        </Alert>
      )}
      
      {/* Agents Tab */}
      {tabValue === 0 && (
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">My Agents</Typography>
            <Box>
              <Button 
                variant="outlined" 
                startIcon={<RefreshIcon />}
                onClick={loadAgents}
                sx={{ mr: 1 }}
                disabled={loading}
              >
                Refresh
              </Button>
              <Button 
                variant="contained" 
                startIcon={<AddIcon />}
                onClick={() => setAgentDialogOpen(true)}
                disabled={loading}
              >
                Create Agent
              </Button>
            </Box>
          </Box>
          
          {/* Loading indicator */}
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          )}
          
          {/* Agent card grid */}
          {!loading && (
            <Grid container spacing={2} sx={{ flexGrow: 1, overflow: 'auto' }}>
              {agents.length === 0 ? (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="body1" color="text.secondary">
                      No agents found. Create your first agent using the "Create Agent" button.
                    </Typography>
                  </Paper>
                </Grid>
              ) : (
                agents.map((agent) => (
                  <Grid item xs={12} sm={6} md={4} key={agent.id}>
                    <Card 
                      variant="outlined" 
                      sx={{ 
                        borderColor: selectedAgent?.id === agent.id ? 'primary.main' : 'divider',
                        boxShadow: selectedAgent?.id === agent.id ? '0 0 0 2px rgba(25, 118, 210, 0.2)' : 'none',
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column'
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          {agent.agent_type === 'nexus' && <MemoryIcon color="primary" sx={{ mr: 1 }} />}
                          {agent.agent_type === 'github' && <GitHubIcon color="primary" sx={{ mr: 1 }} />}
                          {agent.agent_type === 'mail' && <EmailIcon color="primary" sx={{ mr: 1 }} />}
                          {agent.agent_type === 'browser' && <LanguageIcon color="primary" sx={{ mr: 1 }} />}
                          <Typography variant="h6" noWrap>{agent.name}</Typography>
                        </Box>
                        
                        <Typography variant="caption" color="text.secondary">
                          ID: {agent.id} • Type: {agent.agent_type || 'standard'}
                        </Typography>
                        
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {agent.description || `${agent.name} is an AI assistant.`}
                        </Typography>
                        
                        {agent.model_name && (
                          <Chip 
                            label={agent.model_name} 
                            size="small" 
                            sx={{ mt: 1 }}
                          />
                        )}
                      </CardContent>
                      
                      <CardActions>
                        <Button 
                          size="small" 
                          startIcon={<ChatIcon />}
                          onClick={() => {
                            handleAgentSelect(agent);
                            setTabValue(1); // Switch to chat tab
                          }}
                        >
                          Chat
                        </Button>
                        {/* <Button size="small" startIcon={<EditIcon />}>Edit</Button> */}
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => handleDeleteAgent(agent)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </CardActions>
                    </Card>
                  </Grid>
                ))
              )}
            </Grid>
          )}
          
          {/* Create Agent Dialog */}
          <Dialog 
            open={agentDialogOpen} 
            onClose={() => setAgentDialogOpen(false)}
            maxWidth="sm"
            fullWidth
          >
            <DialogTitle>Create New Agent</DialogTitle>
            <DialogContent>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2, mt: 1 }}>
                <TextField 
                  label="Agent Name" 
                  fullWidth 
                  value={newAgentForm.name}
                  onChange={(e) => setNewAgentForm({...newAgentForm, name: e.target.value})}
                />
                
                <TextField 
                  label="Description" 
                  fullWidth 
                  multiline 
                  rows={3}
                  value={newAgentForm.description}
                  onChange={(e) => setNewAgentForm({...newAgentForm, description: e.target.value})}
                  placeholder="A helpful AI assistant"
                />
                
                <FormControl fullWidth>
                  <InputLabel>Agent Type</InputLabel>
                  <Select 
                    label="Agent Type" 
                    value={newAgentForm.agentType}
                    onChange={(e) => setNewAgentForm({...newAgentForm, agentType: e.target.value})}
                  >
                    <MenuItem value="standard">Standard Assistant</MenuItem>
                    <MenuItem value="nexus">Memory-Enabled Agent</MenuItem>
                    <MenuItem value="github">GitHub Agent</MenuItem>
                    <MenuItem value="mail">Email Agent</MenuItem>
                    <MenuItem value="browser">Web Browser Agent</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth>
                  <InputLabel>Model</InputLabel>
                  <Select 
                    label="Model" 
                    value={newAgentForm.model}
                    onChange={(e) => setNewAgentForm({...newAgentForm, model: e.target.value})}
                  >
                    <MenuItem value="">Default Model</MenuItem>
                    <MenuItem value="claude-3-opus">Claude 3 Opus</MenuItem>
                    <MenuItem value="claude-3-sonnet">Claude 3 Sonnet</MenuItem>
                    <MenuItem value="claude-3-haiku">Claude 3 Haiku</MenuItem>
                    <MenuItem value="gpt-4o">GPT-4o</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setAgentDialogOpen(false)}>Cancel</Button>
              <Button 
                variant="contained"
                onClick={handleCreateAgent}
                disabled={!newAgentForm.name || loading}
              >
                {loading ? <CircularProgress size={24} /> : "Create"}
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      )}
      
      {/* Chat Tab */}
      {tabValue === 1 && (
        <Box sx={{ display: 'flex', height: '100%' }}>
          {/* Chat configuration sidebar */}
          <Box sx={{ width: 280, borderRight: '1px solid rgba(0, 0, 0, 0.12)', p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Chat Configuration</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Typography variant="subtitle2" gutterBottom>Selected Agent</Typography>
            {selectedAgent ? (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body1" fontWeight={500}>
                  {selectedAgent.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Type: {selectedAgent.agent_type || 'standard'}
                </Typography>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                No agent selected
              </Typography>
            )}
            
            <FormControl fullWidth sx={{ mb: 1 }}>
              <InputLabel>Change Agent</InputLabel>
              <Select 
                label="Change Agent" 
                value={selectedAgent?.id || ""}
                onChange={(e) => {
                  const agentId = e.target.value;
                  const agent = agents.find(a => a.id === agentId);
                  if (agent) handleAgentSelect(agent);
                }}
                displayEmpty
              >
                <MenuItem value="">Select an agent</MenuItem>
                {agents.map((agent) => (
                  <MenuItem key={agent.id} value={agent.id}>
                    {agent.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Button 
              variant="outlined" 
              startIcon={<AddIcon />} 
              onClick={() => setAgentDialogOpen(true)}
              fullWidth
              sx={{ mb: 3 }}
            >
              Create New Agent
            </Button>
            
            {selectedAgent && selectedAgent.agent_type === 'nexus' && (
              <>
                <Typography variant="subtitle2" gutterBottom>Memory Settings</Typography>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={memoryEnabled} 
                      onChange={(e) => setMemoryEnabled(e.target.checked)}
                    />
                  }
                  label="Enable Memory"
                  sx={{ mb: 3 }}
                />
              </>
            )}
            
            <Typography variant="subtitle2" gutterBottom>Tools</Typography>
            <Box sx={{ mb: 3 }}>
              <Button 
                variant="outlined" 
                startIcon={<AutoAwesomeIcon />}
                fullWidth
                sx={{ mb: 1 }}
                onClick={() => setFeatureRatingMode(true)}
              >
                Rate Features
              </Button>
              <Button 
                variant="outlined" 
                startIcon={<AccountTreeIcon />}
                fullWidth
                onClick={() => setPlanReviewMode(true)}
              >
                Implementation Plan
              </Button>
            </Box>
            
            <Typography variant="caption" color="text.secondary">
              Chat Commands:
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              • !plan - Generate implementation plan
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              • !rate - Rate feature importance
            </Typography>
          </Box>
          
          {/* Main chat area */}
          <Box sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            height: '100%',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Feature rating mode */}
            {featureRatingMode && (
              <Box sx={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                right: 0, 
                bottom: 0, 
                bgcolor: 'background.paper',
                zIndex: 10,
                p: 3,
                display: 'flex',
                flexDirection: 'column'
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Feature Importance Rating</Typography>
                  <Button variant="outlined" onClick={() => setFeatureRatingMode(false)}>
                    Return to Chat
                  </Button>
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  Please rate the importance of each feature for your project from 1-5 stars.
                </Typography>
                
                <List sx={{ flexGrow: 1, overflow: 'auto' }}>
                  {features.map((feature) => (
                    <ListItem key={feature.id} divider>
                      <ListItemText
                        primary={feature.name}
                        secondary={feature.description}
                      />
                      <Box>
                        {[1, 2, 3, 4, 5].map((star) => (
                          <IconButton 
                            key={star}
                            onClick={() => rateFeature(feature.id, star)}
                          >
                            {star <= feature.rating ? (
                              <StarIcon color="primary" />
                            ) : (
                              <StarOutlineIcon />
                            )}
                          </IconButton>
                        ))}
                      </Box>
                    </ListItem>
                  ))}
                </List>
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button 
                    variant="contained"
                    onClick={() => setFeatureRatingMode(false)}
                  >
                    Submit Ratings
                  </Button>
                </Box>
              </Box>
            )}
            
            {/* Plan review mode */}
            {planReviewMode && (
              <Box sx={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                right: 0, 
                bottom: 0, 
                bgcolor: 'background.paper',
                zIndex: 10,
                p: 3,
                display: 'flex',
                flexDirection: 'column'
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">{samplePlan.title}</Typography>
                  <Button variant="outlined" onClick={() => setPlanReviewMode(false)}>
                    Return to Chat
                  </Button>
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  {samplePlan.description}
                </Typography>
                
                <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                  {samplePlan.phases.map((phase, phaseIndex) => (
                    <Paper key={phaseIndex} variant="outlined" sx={{ mb: 2, p: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Phase {phaseIndex + 1}: {phase.name}
                      </Typography>
                      
                      <List dense>
                        {phase.tasks.map((task, taskIndex) => (
                          <ListItem key={taskIndex}>
                            <ListItemIcon>
                              {task.status === 'completed' ? (
                                <CheckCircleIcon color="success" />
                              ) : task.status === 'in-progress' ? (
                                <AutorenewIcon color="primary" />
                              ) : (
                                <RadioButtonUncheckedIcon />
                              )}
                            </ListItemIcon>
                            <ListItemText
                              primary={task.name}
                              secondary={task.status.replace('-', ' ')}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  ))}
                </Box>
                
                <Box sx={{ mt: 2 }}>
                  <TextField
                    label="Feedback on Plan"
                    multiline
                    rows={3}
                    fullWidth
                    sx={{ mb: 2 }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button 
                      variant="contained"
                      onClick={() => setPlanReviewMode(false)}
                    >
                      Submit Feedback
                    </Button>
                  </Box>
                </Box>
              </Box>
            )}
            
            {/* Chat messages */}
            <Box sx={{ 
              flexGrow: 1, 
              overflow: 'auto', 
              p: 2,
              display: 'flex',
              flexDirection: 'column'
            }}>
              {messages.map((msg, index) => (
                <Box 
                  key={index}
                  sx={{
                    display: 'flex',
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                    mb: 2
                  }}
                >
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor: msg.role === 'user' ? 'primary.light' : 'background.paper',
                      color: msg.role === 'user' ? 'white' : 'text.primary',
                      borderRadius: msg.role === 'user' 
                        ? '16px 16px 4px 16px' 
                        : '16px 16px 16px 4px'
                    }}
                  >
                    <Typography variant="body1">
                      {msg.content}
                    </Typography>
                  </Paper>
                </Box>
              ))}
              
              {/* Thinking indicator */}
              {thinking && (
                <Box sx={{ display: 'flex', mb: 2 }}>
                  <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress size={16} sx={{ mr: 1 }} />
                      <Typography variant="body1">Thinking...</Typography>
                    </Box>
                  </Paper>
                </Box>
              )}
              
              {/* Invisible element for scrolling to bottom */}
              <div ref={chatEndRef} />
            </Box>
            
            {/* Input area */}
            <Box sx={{ p: 2, borderTop: '1px solid rgba(0, 0, 0, 0.12)' }}>
              <Box sx={{ display: 'flex' }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Type your message here..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <IconButton 
                        color="primary" 
                        onClick={handleSendMessage}
                        disabled={!chatInput.trim() || thinking || loading}
                      >
                        <SendIcon />
                      </IconButton>
                    )
                  }}
                />
              </Box>
              
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                mt: 1
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                    {selectedAgent ? `Using: ${selectedAgent.name}` : 'No agent selected'}
                  </Typography>
                  
                  {selectedAgent?.agent_type === 'nexus' && (
                    <Chip 
                      size="small" 
                      icon={<MemoryIcon fontSize="small" />} 
                      label={memoryEnabled ? "Memory On" : "Memory Off"}
                      color={memoryEnabled ? "primary" : "default"}
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>
            </Box>
          </Box>
        </Box>
      )}
      
      {/* Documents Tab */}
      {tabValue === 2 && (
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Documentation</Typography>
            <Button variant="contained" startIcon={<AddIcon />}>
              Upload Document
            </Button>
          </Box>
          
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Search Documentation</Typography>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search by keyword, filename, or content..."
              size="small"
              InputProps={{
                endAdornment: (
                  <IconButton color="primary">
                    <SearchIcon />
                  </IconButton>
                )
              }}
            />
          </Paper>
          
          <Typography variant="subtitle1" gutterBottom>Document Collections</Typography>
          
          <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
            <List>
              <ListItem button>
                <ListItemIcon>
                  <FolderSpecialIcon color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="API Documentation" 
                  secondary="12 documents • Last updated: April 8, 2025" 
                />
              </ListItem>
              
              <ListItem button>
                <ListItemIcon>
                  <FolderSpecialIcon color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="User Guides" 
                  secondary="8 documents • Last updated: April 5, 2025" 
                />
              </ListItem>
              
              <ListItem button>
                <ListItemIcon>
                  <FolderSpecialIcon color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Technical Specifications" 
                  secondary="15 documents • Last updated: March 30, 2025" 
                />
              </ListItem>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" sx={{ pl: 2, mb: 1 }}>
                Recent Documents
              </Typography>
              
              {[
                'API Reference v2.1.pdf',
                'System Architecture Diagram.png',
                'Integration Guide.md',
                'Release Notes 3.5.txt',
                'Database Schema.sql'
              ].map((doc, index) => (
                <ListItem button key={index}>
                  <ListItemIcon>
                    {doc.endsWith('.pdf') && <PictureAsPdfIcon color="error" />}
                    {doc.endsWith('.png') && <ImageIcon color="primary" />}
                    {doc.endsWith('.md') && <DescriptionIcon color="primary" />}
                    {doc.endsWith('.txt') && <TextSnippetIcon color="primary" />}
                    {doc.endsWith('.sql') && <StorageIcon color="primary" />}
                  </ListItemIcon>
                  <ListItemText 
                    primary={doc} 
                    secondary={`Last opened: ${new Date(Date.now() - index * 86400000).toLocaleDateString()}`} 
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
      )}
      
      {/* Settings Tab */}
      {tabValue === 3 && (
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Typography variant="h6" gutterBottom>Settings</Typography>
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>Agent Defaults</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Default Agent Type</InputLabel>
                <Select label="Default Agent Type" defaultValue="nexus">
                  <MenuItem value="nexus">Memory-Enabled Agent</MenuItem>
                  <MenuItem value="github">GitHub Agent</MenuItem>
                  <MenuItem value="mail">Email Agent</MenuItem>
                  <MenuItem value="browser">Web Browser Agent</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl fullWidth>
                <InputLabel>Default Model</InputLabel>
                <Select label="Default Model" defaultValue="claude-3-sonnet">
                  <MenuItem value="claude-3-opus">Claude 3 Opus</MenuItem>
                  <MenuItem value="claude-3-sonnet">Claude 3 Sonnet</MenuItem>
                  <MenuItem value="claude-3-haiku">Claude 3 Haiku</MenuItem>
                  <MenuItem value="gpt-4o">GPT-4o</MenuItem>
                </Select>
              </FormControl>
              
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable Memory by Default"
              />
            </Box>
          </Paper>
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>API Configurations</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2 }}>
              <TextField label="GitHub API Token" type="password" fullWidth />
              <TextField label="Email Configuration" fullWidth />
              <TextField label="Web Browser User Agent" fullWidth />
            </Box>
          </Paper>
          
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" gutterBottom>UI Preferences</Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2 }}>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Dark Mode"
              />
              
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Show Agent Recommendations"
              />
              
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable Command Shortcuts"
              />
            </Box>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

// Export the component
export default ErgonView;