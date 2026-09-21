import { useState } from 'react'
import { CityScene } from './components/CityScene'
import { CityInfo } from './components/CityInfo'
import { SignalPanel } from './components/SignalPanel'
import { analyzeDream, type Analysis } from './lib/api'
import './styles/app.css'

const examples = [
  'كنت أمشي وحدي قرب البحر ليلاً تحت المطر، وكان كل شيء أزرق وهادئاً.',
  'I was flying above a golden desert at sunset while a strange red city appeared below.',
  'حلمت بغابة خضراء كثيفة، ضباب خفيف، وبيت بعيد شعرت فيه بالسلام.',
]

export default function App() {
  const [dream, setDream] = useState('')
  const [language, setLanguage] = useState<'auto'|'ar'|'en'>('auto')
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit() {
    if (dream.trim().length < 3) { setError('اكتب بضعة أسطر عن حلمك أولاً.'); return }
    setLoading(true); setError('')
    try { setAnalysis(await analyzeDream(dream, language)) }
    catch (e) { setError(e instanceof Error ? e.message : 'حدث خطأ غير متوقع.') }
    finally { setLoading(false) }
  }

  return <main>
    <header className="topbar"><div className="brand"><span className="brand-mark">✦</span><span>Dream Atlas</span></div><div className="header-note">من حلم مكتوب إلى مدينة يمكن رؤيتها</div></header>
    <section className="hero">
      <div className="hero-copy"><div className="eyebrow">DREAM → SIGNALS → CITY</div><h1>اكتب حلمك.<br/><em>وسنمنحه مدينة.</em></h1><p>محلل ثنائي اللغة يستخرج المشاعر والبيئة والطقس والزمن والأماكن، ثم يبني بصمة مدينة خيالية ويعرضها في مشهد ثلاثي الأبعاد.</p></div>
      <div className="composer panel">
        <div className="composer-head"><span>حلمك</span><select value={language} onChange={e => setLanguage(e.target.value as 'auto'|'ar'|'en')}><option value="auto">اكتشاف اللغة</option><option value="ar">العربية</option><option value="en">English</option></select></div>
        <label className="sr-only" htmlFor="dream-input">نص الحلم</label><textarea id="dream-input" aria-describedby="dream-help" value={dream} onChange={e => setDream(e.target.value)} placeholder="اكتب الحلم كما تتذكره… التفاصيل الصغيرة مفيدة: لون، مكان، شعور، وقت، طقس، شخص أو شيء غريب." dir="auto" />
        <div id="dream-help" className="composer-help">التفاصيل عن المكان واللون والطقس والشعور تساعد المحلل على بناء مدينة أكثر تميّزًا.</div><div className="examples">{examples.map(example => <button key={example} onClick={() => setDream(example)}>{example.slice(0, 44)}…</button>)}</div>
        <button className="primary" type="button" onClick={submit} disabled={loading} aria-busy={loading}>{loading ? 'جارٍ بناء المدينة…' : 'حوّل الحلم إلى مدينة  ↗'}</button>
        {error && <div className="error">{error}</div>}
      </div>
    </section>
    {analysis && <section className="results" aria-live="polite"><div className="result-header"><div><span className="eyebrow">YOUR DREAM CITY</span><h2>هذه هي البصمة التي صنعها حلمك</h2></div><span className="keyword-strip">{analysis.keywords.slice(0,7).map(k => `#${k}`).join('  ')}</span></div><div className="city-layout"><CityScene city={analysis.city} metrics={analysis.metrics} /><CityInfo city={analysis.city} confidence={analysis.confidence} alternatives={analysis.alternatives} /></div><SignalPanel signals={analysis.signals} metrics={analysis.metrics} /></section>}
    <footer>Dream Atlas · مشروع مفتوح المصدر قابل للتوسعة · 240 قالب مدينة مولّد من بيانات</footer>
  </main>
}
