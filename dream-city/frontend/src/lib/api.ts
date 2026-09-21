export type Signal = { category: string; value: string; score: number; evidence: string[] }
export type SceneConfig = { terrain: {type:string;water:boolean;desert:boolean;forest:boolean;mountain:boolean;space:boolean}; city:{scale:number;radius:number;density:number;building_count:number;average_height:number;height_variance:number;street_width:number}; architecture:{style:string;source:string}; roads:{layout:string;style:string;width:number;wetness:number}; water:{enabled:boolean;coverage:number;bridges:number}; vegetation:{type:string;density:number}; sky:{top:string;bottom:string;stars:number;moon:number}; weather:{type:string;rain:number;mist:number;snow:number;storm:number;particles:number}; lighting:{night:number;sunset:number;dawn:number;warmth:number;intensity:number}; landmark:{name:string;fantasy:number;scale:number}; colors:string[]; fantasy:number; atmosphere:string; source_profile:Record<string,number> }
export type City = { id: string; name: string; name_ar: string; tagline: string; tagline_ar: string; score: number; match_reasons: string[]; palette: string[]; terrain: string; architecture: string; road_style: string; atmosphere: string; landmark: string; water: boolean; vegetation: string; density: number; height: number; weather_effect: string; scene_config?: SceneConfig }
export type Metrics = { calmness:number; tension:number; mystery:number; wonder:number; motion:number; sensory_density:number; narrative_depth:number; contradiction_count:number }
export type Analysis = { language: 'ar'|'en'; confidence: number; signals: Signal[]; keywords: string[]; metrics: Metrics; city: City; alternatives: City[] }

// Empty by default so a production build can call the same-origin /api endpoint.
// Local development uses Vite's /api proxy to localhost:8000.
const API_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

export async function analyzeDream(dream: string, language: 'auto'|'ar'|'en'): Promise<Analysis> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 30000)
  let response: Response
  try {
    response = await fetch(`${API_URL}/api/analyze`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({dream, language}), signal: controller.signal })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw new Error('انتهت مهلة التحليل، حاول مرة أخرى.')
    throw new Error('تعذر الاتصال بخدمة التحليل.')
  } finally {
    window.clearTimeout(timeout)
  }
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail ?? 'تعذر تحليل الحلم')
  }
  return response.json()
}
