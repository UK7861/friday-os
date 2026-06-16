import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export const NeuralGraph = ({ data }) => {
  const svgRef = useRef()

  useEffect(() => {
    if (!data) return
    const width = 600
    const height = 400

    const svg = d3.select(svgRef.current)
      .attr('viewBox', [0, 0, width, height])

    svg.selectAll('*').remove()

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(width / 2, height / 2))

    const link = svg.append('g')
      .attr('stroke', '#bc13fe')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke-width', 1)

    const node = svg.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', 5)
      .attr('fill', '#00f5ff')

    simulation.on('tick', () => {
      link.attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y)
      node.attr('cx', d => d.x)
          .attr('cy', d => d.y)
    })
  }, [data])

  return <svg ref={svgRef} className="w-full h-full" />
}
