import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, MeshDistortMaterial } from '@react-three/drei'

const Hologram = () => {
  const meshRef = useRef()
  
  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    meshRef.current.rotation.y = time * 0.5
    meshRef.current.rotation.z = time * 0.2
  })

  return (
    <Sphere ref={meshRef} args={[1, 64, 64]}>
      <MeshDistortMaterial
        color="#00f5ff"
        attach="material"
        distort={0.4}
        speed={2}
        wireframe
        transparent
        opacity={0.6}
      />
    </Sphere>
  )
}

export const HUDCore = () => {
  return (
    <div className="w-full h-full absolute top-0 left-0">
      <Canvas camera={{ position: [0, 0, 3] }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <Hologram />
      </Canvas>
    </div>
  )
}
