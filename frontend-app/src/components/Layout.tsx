import React from 'react';
import { Box } from '@mui/material';
import Navigation from './Navigation';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navigation />
      <Box sx={{ flexGrow: 1, bgcolor: '#f5f5f5' }}>
        {children}
      </Box>
    </Box>
  );
};

export default Layout;