import { Inter } from 'next/font/google'
import Header from '@/components/Header'
import 'styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'SubTrack - Controle suas Assinaturas',
  description: 'Nunca mais perca o controle dos seus pagamentos recorrentes',
}

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  )
}
