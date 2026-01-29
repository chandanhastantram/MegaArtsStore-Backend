import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import ToastContainer from '../common/Toast'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <ToastContainer />
    </div>
  )
}
