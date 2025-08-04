import React from 'react'
import { Layout } from 'antd'
import { ProLayout } from '@ant-design/pro-components'
import { FileTextOutlined, HomeOutlined } from '@ant-design/icons'
import FileUploadPage from './pages/FileUploadPage'
import './App.css'

const { Content } = Layout

const App: React.FC = () => {
  return (
    <ProLayout
      title="证券公司员工配偶信息报备系统"
      logo={<FileTextOutlined />}
      layout="mix"
      navTheme="light"
      headerTheme="light"
      fixedHeader
      fixSiderbar
      colorPrimary="#1890ff"
      route={{
        path: '/',
        routes: [
          {
            path: '/',
            name: '首页',
            icon: <HomeOutlined />,
          },
          {
            path: '/upload',
            name: '文件上传',
            icon: <FileTextOutlined />,
          },
        ],
      }}
      location={{
        pathname: '/',
      }}
      menuItemRender={(item, dom) => (
        <div onClick={() => console.log('导航点击:', item.path)}>
          {dom}
        </div>
      )}
      breadcrumbRender={false}
      menuRender={false}
      headerContentRender={() => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '16px', fontWeight: 500 }}>文件上传与处理</span>
        </div>
      )}
    >
      <Content style={{ margin: '24px', minHeight: 'calc(100vh - 112px)' }}>
        <FileUploadPage />
      </Content>
    </ProLayout>
  )
}

export default App