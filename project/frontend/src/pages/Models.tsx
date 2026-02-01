import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  CircularProgress,
  Alert,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  ModelTraining as ModelIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { modelRegistryAPI } from '../services/api';

interface Model {
  id: string;
  name: string;
  capability_ranks?: any;
  capability_vector?: any;
  max_tokens?: number;
  avg_latency_ms?: number;
  cost_per_1k_usd?: number;
  stake_eth?: number;
  is_verified: boolean;
  trust_score?: number;
  registration_time?: string;
  violations?: number;
}

const Models = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newModel, setNewModel] = useState({
    name: '',
    math: '1',
    code: '1',
    if_rank: '1',
    expert: '1',
    safety: '1',
    max_tokens: '8192',
    avg_latency_ms: '1000',
    cost_per_1k_usd: '0.01',
    stake_eth: '10.0',
  });

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await modelRegistryAPI.getModels();
      console.log('API Response:', response.data);
      if (response.data.success && response.data.data) {
        // 后端直接返回数组，不需要 .models
        const modelsData = Array.isArray(response.data.data) ? response.data.data : [];
        console.log('Models data:', modelsData);
        setModels(modelsData);
      }
    } catch (err) {
      setError('加载模型失败，请稍后重试');
      console.error('Failed to load models:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddModel = async () => {
    try {
      await modelRegistryAPI.registerModel({
        name: newModel.name,
        capability_ranks: {
          math: parseInt(newModel.math),
          code: parseInt(newModel.code),
          if_rank: parseInt(newModel.if_rank),
          expert: parseInt(newModel.expert),
          safety: parseInt(newModel.safety),
        },
        max_tokens: parseInt(newModel.max_tokens),
        avg_latency_ms: parseInt(newModel.avg_latency_ms),
        cost_per_1k_usd: parseFloat(newModel.cost_per_1k_usd),
        stake_eth: parseFloat(newModel.stake_eth),
      });

      setOpenDialog(false);
      setNewModel({
        name: '',
        math: '',
        code: '',
        if_rank: '',
        expert: '',
        safety: '',
        max_tokens: '',
        avg_latency_ms: '',
        cost_per_1k_usd: '',
        stake_eth: '',
      });
      loadModels();
    } catch (err) {
      setError('添加模型失败，请稍后重试');
      console.error('Failed to add model:', err);
    }
  };

  const handleVerifyModel = async (modelId: string) => {
    try {
      await modelRegistryAPI.verifyModel(modelId);
      loadModels();
    } catch (err) {
      setError('验证模型失败，请稍后重试');
      console.error('Failed to verify model:', err);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: 'background.default',
        py: 4,
      }}
    >
      <Container maxWidth="xl">
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            模型管理
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            sx={{
              px: 3,
              py: 1.5,
              background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
              },
            }}
          >
            添加模型
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress size={40} />
          </Box>
        ) : models.length === 0 ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 12,
              backgroundColor: 'background.paper',
              borderRadius: 3,
            }}
          >
            <ModelIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 3 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              暂无模型
            </Typography>
            <Typography variant="body2" color="text.secondary">
              点击"添加模型"按钮开始添加您的第一个模型
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {models.map((model) => (
              <Grid item xs={12} sm={6} md={4} key={model.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: 'background.paper',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 24px rgba(0, 0, 0, 0.15)',
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <ModelIcon sx={{ fontSize: 32, color: 'primary.main', mr: 1.5 }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" component="h2" gutterBottom>
                          {model.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {model.trust_score && `信任分数: ${model.trust_score.toFixed(2)}`}
                          {model.max_tokens && ` | 最大令牌: ${model.max_tokens}`}
                          {model.avg_latency_ms && ` | 延迟: ${model.avg_latency_ms}ms`}
                        </Typography>
                      </Box>
                      {model.is_verified ? (
                        <CheckIcon sx={{ color: 'success.main', fontSize: 24 }} />
                      ) : (
                        <ErrorIcon sx={{ color: 'warning.main', fontSize: 24 }} />
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {model.capability_ranks && Object.keys(model.capability_ranks).length > 0 && (
                        Object.entries(model.capability_ranks).map(([key, value]) => (
                          <Chip
                            key={key}
                            label={`${key}: ${value}`}
                            size="small"
                            sx={{
                              backgroundColor: alpha('#3b82f6', 0.1),
                              color: '#60a5fa',
                              border: '1px solid rgba(59, 130, 246, 0.2)',
                            }}
                          />
                        ))
                      )}
                      {model.violations !== undefined && model.violations > 0 && (
                        <Chip
                          label={`违规次数: ${model.violations}`}
                          size="small"
                          sx={{
                            backgroundColor: alpha('#ef4444', 0.1),
                            color: '#f87171',
                            border: '1px solid rgba(239, 68, 68, 0.2)',
                          }}
                        />
                      )}
                    </Box>
                  </CardContent>
                  <CardActions sx={{ px: 2, pb: 2 }}>
                    {!model.is_verified && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleVerifyModel(model.id)}
                        sx={{ borderRadius: 2 }}
                      >
                        验证模型
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        <Dialog
          open={openDialog}
          onClose={() => setOpenDialog(false)}
          maxWidth="md"
          fullWidth
          PaperProps={{
            sx: {
              backgroundColor: 'background.paper',
              borderRadius: 3,
            },
          }}
        >
          <DialogTitle>添加新模型</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="模型名称"
              fullWidth
              variant="outlined"
              value={newModel.name}
              onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>能力排名 (正整数)</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="数学排名"
                  type="number"
                  inputProps={{ min: 1, step: 1 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.math}
                  onChange={(e) => setNewModel({ ...newModel, math: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="代码排名"
                  type="number"
                  inputProps={{ min: 1, step: 1 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.code}
                  onChange={(e) => setNewModel({ ...newModel, code: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="推理排名"
                  type="number"
                  inputProps={{ min: 1, step: 1 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.if_rank}
                  onChange={(e) => setNewModel({ ...newModel, if_rank: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="专家排名"
                  type="number"
                  inputProps={{ min: 1, step: 1 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.expert}
                  onChange={(e) => setNewModel({ ...newModel, expert: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  margin="dense"
                  label="安全排名"
                  type="number"
                  inputProps={{ min: 1, step: 1 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.safety}
                  onChange={(e) => setNewModel({ ...newModel, safety: e.target.value })}
                />
              </Grid>
            </Grid>
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>性能参数</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="最大令牌数"
                  type="number"
                  fullWidth
                  variant="outlined"
                  value={newModel.max_tokens}
                  onChange={(e) => setNewModel({ ...newModel, max_tokens: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="平均延迟 (ms)"
                  type="number"
                  fullWidth
                  variant="outlined"
                  value={newModel.avg_latency_ms}
                  onChange={(e) => setNewModel({ ...newModel, avg_latency_ms: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="成本 (USD/1K tokens)"
                  type="number"
                  inputProps={{ step: 0.0001 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.cost_per_1k_usd}
                  onChange={(e) => setNewModel({ ...newModel, cost_per_1k_usd: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="质押 (ETH)"
                  type="number"
                  inputProps={{ step: 0.0001 }}
                  fullWidth
                  variant="outlined"
                  value={newModel.stake_eth}
                  onChange={(e) => setNewModel({ ...newModel, stake_eth: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={() => setOpenDialog(false)} sx={{ borderRadius: 2 }}>
              取消
            </Button>
            <Button
              onClick={handleAddModel}
              variant="contained"
              disabled={!newModel.name}
              sx={{ borderRadius: 2 }}
            >
              添加
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default Models;
