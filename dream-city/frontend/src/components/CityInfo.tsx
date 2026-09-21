import type { City } from '../lib/api'

export function CityInfo({ city, confidence, alternatives }: {city: City; confidence:number; alternatives: City[]}) {
  return <section className="panel city-info">
    <div className="section-kicker">02 · المدينة الناتجة</div>
    <div className="city-title-row"><div><h1>{city.name_ar}</h1><p>{city.name} · {city.tagline}</p></div><div className="confidence"><b>{Math.round(confidence*100)}%</b><span>ثقة المطابقة</span></div></div>
    <p className="lead">{city.tagline_ar}</p>
    <div className="reason-list">{city.match_reasons.map(reason => <span key={reason}>{reason}</span>)}</div>
    <div className="city-specs"><div><small>البيئة</small><b>{city.terrain}</b></div><div><small>العمارة</small><b>{city.architecture}</b></div><div><small>الجو</small><b>{city.weather_effect}</b></div><div><small>المعلم</small><b>{city.landmark}</b></div><div><small>التخطيط</small><b>{city.scene_config?.roads.layout}</b></div><div><small>الخيال</small><b>{Math.round((city.scene_config?.fantasy ?? 0) * 100)}%</b></div></div>
    <div className="palette">{city.palette.map(color => <i key={color} style={{background:color}} title={color} />)}</div>
    <div className="alternatives"><h3>مدن قريبة من بصمة حلمك</h3>{alternatives.map(item => <div className="alternative" key={item.id}><span>{item.name_ar}</span><b>{Math.round(item.score*100)}%</b></div>)}</div>
  </section>
}
