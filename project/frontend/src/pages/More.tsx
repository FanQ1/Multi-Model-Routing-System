import React from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  alpha,
} from '@mui/material';
import {
  Construction as ConstructionIcon,
} from '@mui/icons-material';

const More = () => {
  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px)',
        backgroundColor: 'background.default',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Container maxWidth="md">
        <Card
          sx={{
            backgroundColor: 'background.paper',
            borderRadius: 3,
            textAlign: 'center',
            py: 8,
          }}
        >
          <CardContent>
            <ConstructionIcon
              sx={{
                fontSize: 80,
                color: 'text.secondary',
                mb: 3,
                opacity: 0.5,
              }}
            />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
              功能开发中
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              更多精彩功能即将上线，敬请期待
            </Typography>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                gap: 2,
                flexWrap: 'wrap',
              }}
            >
              {[
                '数据分析',
                '模型评估',
                '性能监控',
                '日志审计',
                '权限管理',
              ].map((feature) => (
                <Box
                  key={feature}
                  sx={{
                    px: 3,
                    py: 1.5,
                    borderRadius: 2,
                    backgroundColor: alpha('#3b82f6', 0.1),
                    color: '#60a5fa',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                  }}
                >
                  <Typography variant="body2">{feature}</Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default More;
