import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Detailed, OrbitControls, Sparkles, Stars } from '@react-three/drei'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'
import type { City, Metrics } from '../lib/api'

type SceneConfig = NonNullable<City['scene_config']>
function colorAt(colors: string[], index: number, fallback: string) { return colors[index] ?? fallback }

function BuildingInstances({ config, colors }: { config: SceneConfig; colors: string[] }) {
  const ref = useRef<THREE.InstancedMesh>(null)
  const { size } = useThree()
  const mobile = size.width < 700
  const count = Math.min(mobile ? 46 : 82, Math.max(mobile ? 18 : 24, config.city.building_count))
  const layout = useMemo(() => Array.from({ length: count }, (_, i) => {
    const angle = (i / count) * Math.PI * 2 * (1 + (i % 3) * 0.07)
    const radius = 2.2 + ((i * 17) % 100) / 100 * Math.max(3, config.city.radius - 2.5)
    const h = config.city.average_height * (0.58 + ((i * 29) % 100) / 100 * config.city.height_variance * 1.35)
    return { x: Math.cos(angle) * radius, z: Math.sin(angle) * radius, h, w: 0.45 + ((i * 11) % 100) / 100 * (0.35 + config.city.density * 0.55) }
  }), [count, config])
  const matrix = useMemo(() => new THREE.Object3D(), [])
  if (ref.current) {
    layout.forEach((b, i) => {
      matrix.position.set(b.x * config.city.scale, b.h / 2, b.z * config.city.scale)
      matrix.rotation.set(0, (i % 7) * 0.15, 0)
      matrix.scale.set(b.w, b.h, b.w)
      matrix.updateMatrix(); ref.current!.setMatrixAt(i, matrix.matrix)
      ref.current!.setColorAt(i, new THREE.Color(colorAt(colors, i % Math.max(1, colors.length), '#9fb6d6')))
    })
    ref.current.instanceMatrix.needsUpdate = true
    if (ref.current.instanceColor) ref.current.instanceColor.needsUpdate = true
  }
  const style = config.architecture.style
  return <instancedMesh ref={ref} args={[undefined, undefined, count]} castShadow={false} receiveShadow={false}>
    {style === 'organic' || style === 'tower' || style === 'floating' ? <cylinderGeometry args={[0.55, 0.72, 1, mobile ? 5 : style === 'organic' ? 7 : 6]} /> : <boxGeometry args={[1, 1, 1]} />}
    <meshStandardMaterial roughness={style === 'crystal' ? 0.24 : 0.62} metalness={style === 'crystal' || style === 'floating' ? 0.35 : 0.08} />
  </instancedMesh>
}

function Roads({ config, colors }: { config: SceneConfig; colors: string[] }) {
  const width = config.roads.width; const roadColor = config.roads.wetness > 0.45 ? colorAt(colors, 0, '#14243b') : '#182536'; const material = <meshStandardMaterial color={roadColor} roughness={config.roads.wetness > 0.45 ? 0.2 : 0.72} metalness={config.roads.wetness > 0.45 ? 0.3 : 0.05} />
  return <group position={[0, 0.035, 0]}>
    <mesh rotation={[-Math.PI / 2, 0, 0]}>{<planeGeometry args={[config.city.radius * 2.2, width]} />}{material}</mesh>
    {config.roads.layout === 'grid' || config.roads.layout === 'grid_stone' ? <mesh rotation={[-Math.PI / 2, 0, Math.PI / 2]}><planeGeometry args={[config.city.radius * 2.2, width]} />{material}</mesh> : <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}><torusGeometry args={[config.city.radius * 0.52, width * 0.42, 8, 48]} />{material}</mesh>}
  </group>
}

function WaterAndBridges({ config, colors }: { config: SceneConfig; colors: string[] }) {
  if (!config.water.enabled) return null
  const water = colorAt(colors, 1, '#1d5b7d')
  return <group><mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.015, 0]}><circleGeometry args={[config.city.radius * config.water.coverage * 1.9, 48]} /><meshStandardMaterial color={water} roughness={0.12} metalness={0.58} transparent opacity={0.78} /></mesh>{Array.from({ length: Math.min(3, config.water.bridges) }, (_, i) => <mesh key={i} position={[-config.city.radius * 0.38 + i * config.city.radius * 0.36, 0.24 + i * 0.02, 0]}><boxGeometry args={[config.city.radius * 0.48, 0.18, 0.72]} /><meshStandardMaterial color={colorAt(colors, 3, '#cbd8e5')} roughness={0.45} /></mesh>)}</group>
}

function Vegetation({ config }: { config: SceneConfig }) {
  const count = Math.round(config.vegetation.density * 40)
  const data = useMemo(() => Array.from({ length: count }, (_, i) => { const a = i * 2.399; const r = 4.5 + (i % 9) * 0.48; return [Math.cos(a) * r, 0.42, Math.sin(a) * r] as [number, number, number] }), [count])
  return count ? <group>{data.map((p, i) => <mesh key={i} position={p} scale={[0.45 + (i % 3) * 0.12, 0.75 + (i % 4) * 0.2, 0.45 + (i % 3) * 0.12]}><coneGeometry args={[0.65, 1.8, 6]} /><meshStandardMaterial color={config.terrain.desert ? '#a9824a' : '#4e8a68'} roughness={0.9} /></mesh>)}</group> : null
}

function Landmark({ config, colors }: { config: SceneConfig; colors: string[] }) {
  const group = useRef<THREE.Group>(null); const scale = config.landmark.scale; const color = colorAt(colors, 2, '#c9b8ff')
  useFrame(({ camera }) => { if (group.current) group.current.visible = camera.position.distanceTo(new THREE.Vector3(0, 0, 0)) < 45 })
  const high = config.architecture.style === 'dome'
    ? <mesh><sphereGeometry args={[0.9, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2]} /><meshStandardMaterial color={color} /></mesh>
    : config.architecture.style === 'crystal'
      ? <mesh><octahedronGeometry args={[1, 1]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={config.fantasy * 0.7} metalness={0.35} roughness={0.2} /></mesh>
      : <mesh><cylinderGeometry args={[0.34, 0.72, 2.4, 8]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={config.fantasy * 0.7} /></mesh>
  return <group ref={group} position={[0, 1.1 * scale, 0]} scale={scale}><Detailed distances={[0, 16, 30]}><group>{high}</group><group><mesh><boxGeometry args={[0.9, 1.8, 0.9]} /><meshStandardMaterial color={color} /></mesh></group><group><mesh><boxGeometry args={[0.8, 1.2, 0.8]} /><meshStandardMaterial color={color} /></mesh></group></Detailed></group>
}

function Weather({ config, colors }: { config: SceneConfig; colors: string[] }) {
  const count = config.weather.particles
  if (config.terrain.space) return <><Stars radius={36} depth={20} count={Math.min(1000, 350 + count)} factor={2.1} saturation={0} fade speed={0.35} /><Sparkles count={Math.min(180, 50 + Math.round(count * 0.45))} scale={[18, 10, 18]} size={1.5} speed={0.18} color={colorAt(colors, 2, '#9edcff')} /></>
  if (config.weather.rain > 0.45) return <Sparkles count={Math.min(240, Math.round(count * 0.9))} scale={[18, 10, 18]} size={1.15} speed={2.1} color={colorAt(colors, 3, '#cce9ff')} />
  if (config.weather.snow > 0.35) return <Sparkles count={Math.min(190, Math.round(count * 0.7))} scale={[18, 10, 18]} size={2.2} speed={0.45} color="#fff" />
  return <Sparkles count={Math.min(120, Math.round(count * 0.45))} scale={[18, 8, 18]} size={1.6} speed={0.22} color={colorAt(colors, 2, '#d7e9ff')} />
}

function CityGeometry({ city, metrics }: { city: City; metrics: Metrics }) {
  const group = useRef<THREE.Group>(null); const config = city.scene_config!; const colors = config.colors
  useFrame((_, delta) => { if (group.current) group.current.rotation.y += delta * (0.006 + config.fantasy * 0.006) })
  const terrainColor = config.terrain.desert ? '#8a6540' : config.terrain.forest ? '#203b32' : colorAt(colors, 0, '#091B3A')
  return <group ref={group} scale={config.city.scale}>
    <mesh rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[config.city.radius * 1.35, 48]} /><meshStandardMaterial color={terrainColor} roughness={0.9} /></mesh>
    <Roads config={config} colors={colors} /><WaterAndBridges config={config} colors={colors} /><BuildingInstances config={config} colors={colors} /><Vegetation config={config} /><Landmark config={config} colors={colors} /><Weather config={config} colors={colors} />
    {config.sky.moon > 0.35 && <mesh position={[5, 8, -8]}><sphereGeometry args={[0.48 + config.sky.moon * 0.35, 16, 16]} /><meshBasicMaterial color={colorAt(colors, 3, '#fff1c7')} /></mesh>}
    <pointLight position={[0, 3.2, 0]} color={colorAt(colors, 2, '#a9c8ff')} intensity={1.2 + metrics.wonder * 3.2} distance={14} />
  </group>
}

export function CityScene({ city, metrics }: { city: City; metrics: Metrics }) {
  const config = city.scene_config
  if (!config) return <div className="scene-shell scene-fallback" role="img" aria-label="تعذر تحميل مشهد المدينة">Scene configuration unavailable.</div>
  const background = config.sky.top
  return <div className="scene-shell" role="img" aria-label={`مشهد ثلاثي الأبعاد لمدينة ${city.name_ar}`}>
    <Canvas dpr={[1, 1.35]} gl={{ antialias: false, powerPreference: 'high-performance' }} camera={{ position: [12, 8, 14], fov: 45 }}>
      <color attach="background" args={[background]} /><fog attach="fog" args={[background, 14, 48 / (1 + config.weather.mist * 1.8)]} />
      <ambientLight intensity={0.42 + config.lighting.intensity * 0.16} /><directionalLight position={[8, 12, 6]} intensity={config.lighting.night > 0.55 ? 0.65 : 1.8} />
      <CityGeometry city={city} metrics={metrics} /><OrbitControls enablePan={false} minDistance={7} maxDistance={28} maxPolarAngle={Math.PI * 0.48} enableDamping dampingFactor={0.08} />
    </Canvas><div className="scene-hint">اسحب للتدوير · عجلة للتقريب</div>
  </div>
}
