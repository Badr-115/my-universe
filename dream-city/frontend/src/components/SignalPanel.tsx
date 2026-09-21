import type { Metrics, Signal } from '../lib/api'

const labels: Record<string,string> = { emotion:'المشاعر', color:'الألوان', weather:'الطقس', time:'الوقت', environment:'البيئة', place:'الأماكن', dream_type:'نوع الحلم', motion:'الحركة', entity:'العناصر', light:'الإضاءة', mood:'الأجواء', keyword:'الكلمات' }
const metricLabels: Record<string,string> = { calmness:'الهدوء', tension:'التوتر', mystery:'الغموض', wonder:'الدهشة', motion:'الحركة', sensory_density:'الكثافة الحسية' }

export function SignalPanel({ signals, metrics }: { signals: Signal[]; metrics: Metrics }) {
  const grouped = signals.reduce<Record<string, Signal[]>>((acc, signal) => { (acc[signal.category] ??= []).push(signal); return acc }, {})
  return <section className="panel signal-panel">
    <div className="section-kicker">01 · تحليل الحلم</div>
    <h2>البصمة التي استخرجها المحلل</h2>
    <div className="metric-grid">{Object.entries(metricLabels).map(([key,label]) => <div className="metric-card" key={key}><span>{label}</span><b>{Math.round((metrics[key as keyof Metrics] as number) * 100)}%</b><div className="meter"><i style={{width:`${Math.max(4,(metrics[key as keyof Metrics] as number)*100)}%`}} /></div></div>)}</div>
    {metrics.contradiction_count > 0 && <div className="contrast-note">الحلم يحتوي على {metrics.contradiction_count} تعارضًا دلاليًا؛ تم الاحتفاظ بها كمكوّن من هوية المدينة بدل إسقاط أحد العناصر.</div>}
    <div className="signal-grid">
      {Object.entries(grouped).map(([category, items]) => <div className="signal-card" key={category}>
        <span>{labels[category] ?? category}</span>
        {items.slice(0,4).map(item => <div className="signal-row" key={`${category}-${item.value}`}><div><strong>{item.value}</strong><small>{item.evidence.join(' · ')}</small></div><div className="meter"><i style={{width:`${Math.max(8,item.score*100)}%`}} /></div></div>)}
      </div>)}
    </div>
  </section>
}
