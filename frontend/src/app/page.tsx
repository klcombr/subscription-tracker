'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import styles from '@/styles/Home.module.css'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export default function Home() {
  const [stats, setStats] = useState<any>(null)
  const [subscriptions, setSubscriptions] = useState([])
  const [categories, setCategories] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [loading, setLoading] = useState(true)

  // Form state
  const [formData, setFormData] = useState({
    name: '', price: '', frequency: 'monthly', category_id: '', next_due_date: ''
  })

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const [statsRes, subsRes, catsRes] = await Promise.all([
        axios.get(`${API_URL}/subscriptions/dashboard/stats`),
        axios.get(`${API_URL}/subscriptions/`),
        axios.get(`${API_URL}/categories/`)
      ])
      setStats(statsRes.data)
      setSubscriptions(subsRes.data)
      setCategories(catsRes.data)
    } catch (err) {
      console.error('Erro ao carregar dados:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      await axios.post(`${API_URL}/subscriptions/`, {
        ...formData,
        price: parseFloat(formData.price),
        category_id: parseInt(formData.category_id)
      })
      setShowAddModal(false)
      setFormData({ name: '', price: '', frequency: 'monthly', category_id: '', next_due_date: '' })
      fetchData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao salvar')
    }
  }

  async function toggleStatus(id: number) {
    await axios.patch(`${API_URL}/subscriptions/${id}/toggle`)
    fetchData()
  }

  async function deleteSubscription(id: number) {
    if (!confirm('Tem certeza que deseja remover esta assinatura?')) return
    await axios.delete(`${API_URL}/subscriptions/${id}`)
    fetchData()
  }

  if (loading) return <div className={styles.center}><p>Carregando...</p></div>

  return (
    <div className={styles.container}>
      {/* Stats Cards */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Gasto Mensal</span>
          <span className={styles.statValue}>R$ {stats?.total_monthly_spending?.toFixed(2)}</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Gasto Anual</span>
          <span className={styles.statValue}>R$ {stats?.total_yearly_spending?.toFixed(2)}</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Assinaturas Ativas</span>
          <span className={styles.statValue}>{stats?.active_subscriptions}</span>
        </div>
        {stats?.top_category && (
          <div className={styles.statCard}>
            <span className={styles.statLabel}>Maior Gasto</span>
            <span className={styles.statValue}>{stats.top_category}</span>
          </div>
        )}
      </div>

      {/* Upcoming Renewals */}
      {stats?.upcoming_renewals?.length > 0 && (
        <section className={styles.section}>
          <h2>Próximos Vencimentos</h2>
          <div className={styles.renewalsList}>
            {stats.upcoming_renewals.map((r: any) => (
              <div key={r.id} className={styles.renewalItem}>
                <div className={styles.renewalInfo}>
                  <strong>{r.name}</strong>
                  <span className={styles.renewalCat} style={{ borderLeftColor: r.category_color }}>{r.category_name}</span>
                </div>
                <div className={styles.renewalMeta}>
                  <span className={styles.renewalDays}>{r.days_until ?? 0} dias</span>
                  <span className={styles.renewalPrice}>R$ {r.price.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Subscriptions List */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2>Suas Assinaturas</h2>
          <button onClick={() => setShowAddModal(true)} className={styles.addBtn}>+ Nova</button>
        </div>
        
        <div className={styles.subsGrid}>
          {subscriptions.length === 0 ? (
            <p className={styles.empty}>Nenhuma assinatura cadastrada. Adicione sua primeira!</p>
          ) : (
            subscriptions.map((sub: any) => (
              <div key={sub.id} className={`${styles.subCard} ${!sub.is_active ? styles.inactive : ''}`}>
                <div className={styles.subHeader}>
                  <span className={styles.subDot} style={{ background: sub.category_color }} />
                  <h3>{sub.name}</h3>
                  <span className={styles.subFreq}>{sub.frequency === 'monthly' ? 'Mensal' : 'Anual'}</span>
                </div>
                <div className={styles.subBody}>
                  <p className={styles.subPrice}>R$ {sub.price.toFixed(2)}</p>
                  <p className={styles.subDue}>Vence em {sub.next_due_date && new Date(sub.next_due_date).toLocaleDateString('pt-BR')}</p>
                  {sub.description && <p className={styles.subDesc}>{sub.description}</p>}
                </div>
                <div className={styles.subActions}>
                  <button onClick={() => toggleStatus(sub.id)} className={styles.toggleBtn}>
                    {sub.is_active ? 'Desativar' : 'Ativar'}
                  </button>
                  <button onClick={() => deleteSubscription(sub.id)} className={styles.deleteBtn}>Excluir</button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Add Modal */}
      {showAddModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2>Nova Assinatura</h2>
            <form onSubmit={handleSubmit}>
              <input placeholder="Nome (ex: Netflix)" required value={formData.name}
                onChange={e => setFormData({...formData, name: e.target.value})} />
              <input type="number" step="0.01" placeholder="Preço (R$)" required value={formData.price}
                onChange={e => setFormData({...formData, price: e.target.value})} />
              <select value={formData.frequency} onChange={e => setFormData({...formData, frequency: e.target.value})}>
                <option value="monthly">Mensal</option>
                <option value="yearly">Anual</option>
              </select>
              <select required value={formData.category_id}
                onChange={e => setFormData({...formData, category_id: e.target.value})}>
                <option value="">Selecione uma categoria</option>
                {categories.map((c: any) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
              <input type="date" required value={formData.next_due_date}
                onChange={e => setFormData({...formData, next_due_date: e.target.value})} />
              <div className={styles.modalActions}>
                <button type="button" onClick={() => setShowAddModal(false)} className={styles.cancelBtn}>Cancelar</button>
                <button type="submit" className={styles.saveBtn}>Salvar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
