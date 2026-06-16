import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export const ProductionNeuralGraph = ({ data }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.nodes) return;
    
    const width = 800;
    const height = 500;
    
    const svg = d3.select(svgRef.current)
      .attr('viewBox', [0, 0, width, height])
      .style('background', 'transparent');

    svg.selectAll('*').remove();

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', '#00f5ff')
      .attr('stroke-opacity', 0.4)
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '5,5');

    const node = svg.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('circle')
      .attr('r', 8)
      .attr('fill', d => d.type === 'CORE' ? '#bc13fe' : '#00f5ff')
      .attr('filter', 'drop-shadow(0 0 5px #00f5ff)');

    node.append('text')
      .text(d => d.id)
      .attr('x', 12)
      .attr('y', 4)
      .style('fill', '#fff')
      .style('font-family', 'JetBrains Mono')
      .style('font-size', '10px');

    simulation.on('tick', () => {
      link.attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }
    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }
    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  }, [data]);

  return <svg ref={svgRef} className="w-full h-full" />;
};
