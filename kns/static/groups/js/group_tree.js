// Use container dimensions dynamically
var container = d3.select('#group_tree');
var containerWidth = container.node().getBoundingClientRect().width;
var containerHeight = container.node().getBoundingClientRect().height;

// Set margins
const margin = { top: 20, right: 120, bottom: 20, left: 120 };
const width = containerWidth - margin.right - margin.left;
const height = containerHeight - margin.top - margin.bottom;

var root = {
  name: 'Flare',
  children: [
    {
      name: 'Analytics',
      children: [
        {
          name: 'cluster',
          children: [
            {
              name: 'AgglomerativeCluster',
              size: 3938,
            },
            {
              name: 'CommunityStructure',
              size: 3812,
            },
            {
              name: 'HierarchicalCluster',
              size: 6714,
            },
            {
              name: 'MergeEdge',
              size: 743,
            },
          ],
        },
        {
          name: 'graph',
          children: [
            {
              name: 'BetweennessCentrality',
              size: 3534,
            },
            {
              name: 'LinkDistance',
              size: 5731,
            },
            {
              name: 'MaxFlowMinCut',
              size: 7840,
            },
            {
              name: 'ShortestPaths',
              size: 5914,
            },
            {
              name: 'SpanningTree',
              size: 3416,
            },
          ],
        },
        {
          name: 'optimization',
          children: [
            {
              name: 'AspectRatioBanker',
              size: 7074,
            },
          ],
        },
      ],
    },
    {
      name: 'animate',
      children: [
        {
          name: 'Easing',
          size: 17010,
        },
        {
          name: 'FunctionSequence',
          size: 5842,
        },
        {
          name: 'interpolate',
          children: [
            {
              name: 'ArrayInterpolator',
              size: 1983,
            },
            {
              name: 'ColorInterpolator',
              size: 2047,
            },
            {
              name: 'DateInterpolator',
              size: 1375,
            },
            {
              name: 'Interpolator',
              size: 8746,
            },
            {
              name: 'MatrixInterpolator',
              size: 2202,
            },
            {
              name: 'NumberInterpolator',
              size: 1382,
            },
            {
              name: 'ObjectInterpolator',
              size: 1629,
            },
            {
              name: 'PointInterpolator',
              size: 1675,
            },
            {
              name: 'RectangleInterpolator',
              size: 2042,
            },
          ],
        },
        {
          name: 'ISchedulable',
          size: 1041,
        },
        {
          name: 'Parallel',
          size: 5176,
        },
        {
          name: 'Pause',
          size: 449,
        },
        {
          name: 'Scheduler',
          size: 5593,
        },
        {
          name: 'Sequence',
          size: 5534,
        },
        {
          name: 'Transition',
          size: 9201,
        },
        {
          name: 'Transitioner',
          size: 19975,
        },
        {
          name: 'TransitionEvent',
          size: 1116,
        },
        {
          name: 'Tween',
          size: 6006,
        },
      ],
    },
    {
      name: 'data',
      children: [
        {
          name: 'converters',
          children: [
            {
              name: 'Converters',
              size: 721,
            },
            {
              name: 'DelimitedTextConverter',
              size: 4294,
            },
            {
              name: 'GraphMLConverter',
              size: 9800,
            },
            {
              name: 'IDataConverter',
              size: 1314,
            },
            {
              name: 'JSONConverter',
              size: 2220,
            },
          ],
        },
        {
          name: 'DataField',
          size: 1759,
        },
        {
          name: 'DataSchema',
          size: 2165,
        },
        {
          name: 'DataSet',
          size: 586,
        },
        {
          name: 'DataSource',
          size: 3331,
        },
        {
          name: 'DataTable',
          size: 772,
        },
        {
          name: 'DataUtil',
          size: 3322,
        },
      ],
    },
    {
      name: 'display',
      children: [
        {
          name: 'DirtySprite',
          size: 8833,
        },
        {
          name: 'LineSprite',
          size: 1732,
        },
        {
          name: 'RectSprite',
          size: 3623,
        },
        {
          name: 'TextSprite',
          size: 10066,
        },
      ],
    },
  ],
};

var i = 0,
  duration = 750,
  rectW = 60,
  rectH = 30;

var tree = d3.layout.tree().nodeSize([70, 40]);
var diagonal = d3.svg.diagonal().projection(function (d) {
  return [d.x + rectW / 2, d.y + rectH / 2];
});

var svg = d3
  .select('#group_tree')
  .append('svg')
  .attr('width', '100%')
  .attr('height', '100vh')
  .call((zm = d3.behavior.zoom().scaleExtent([1, 2]).on('zoom', redraw)))
  .append('g')
  .attr('transform', 'translate(' + 350 + ',' + 20 + ')');

//necessary so that zoom knows where to zoom and unzoom from
zm.translate([350, 20]);

root.x0 = 0;
root.y0 = height / 2;

function collapse(d) {
  if (d.children) {
    d._children = d.children;
    d._children.forEach(collapse);
    d.children = null;
  }
}

root.children.forEach(collapse);
update(root);

d3.select('#body').style('height', '800px');

function update(source) {
  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
    links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function (d) {
    d.y = d.depth * 180;
  });

  // Update the nodes…
  var node = svg.selectAll('g.node').data(nodes, function (d) {
    return d.id || (d.id = ++i);
  });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('transform', function (d) {
      return 'translate(' + source.x0 + ',' + source.y0 + ')';
    })
    .on('click', click);

  nodeEnter
    .append('rect')
    .attr('width', rectW)
    .attr('height', rectH)
    .attr('stroke', 'black')
    .attr('stroke-width', 1)
    .style('fill', function (d) {
      return d._children ? 'lightsteelblue' : '#fff';
    });

  nodeEnter
    .append('text')
    .attr('x', rectW / 2)
    .attr('y', rectH / 2)
    .attr('dy', '.35em')
    .attr('text-anchor', 'middle')
    .text(function (d) {
      return d.name;
    });

  // Transition nodes to their new position.
  var nodeUpdate = node
    .transition()
    .duration(duration)
    .attr('transform', function (d) {
      return 'translate(' + d.x + ',' + d.y + ')';
    });

  nodeUpdate
    .select('rect')
    .attr('width', rectW)
    .attr('height', rectH)
    .attr('stroke', 'black')
    .attr('stroke-width', 1)
    .style('fill', function (d) {
      return d._children ? 'lightsteelblue' : '#fff';
    });

  nodeUpdate.select('text').style('fill-opacity', 1);

  // Transition exiting nodes to the parent's new position.
  var nodeExit = node
    .exit()
    .transition()
    .duration(duration)
    .attr('transform', function (d) {
      return 'translate(' + source.x + ',' + source.y + ')';
    })
    .remove();

  nodeExit
    .select('rect')
    .attr('width', rectW)
    .attr('height', rectH)
    //.attr("width", bbox.getBBox().width)""
    //.attr("height", bbox.getBBox().height)
    .attr('stroke', 'black')
    .attr('stroke-width', 1);

  nodeExit.select('text');

  // Update the links…
  var link = svg.selectAll('path.link').data(links, function (d) {
    return d.target.id;
  });

  // Enter any new links at the parent's previous position.
  link
    .enter()
    .insert('path', 'g')
    .attr('class', 'link')
    .attr('x', rectW / 2)
    .attr('y', rectH / 2)
    .attr('d', function (d) {
      var o = {
        x: source.x0,
        y: source.y0,
      };
      return diagonal({
        source: o,
        target: o,
      });
    });

  // Transition links to their new position.
  link.transition().duration(duration).attr('d', diagonal);

  // Transition exiting nodes to the parent's new position.
  link
    .exit()
    .transition()
    .duration(duration)
    .attr('d', function (d) {
      var o = {
        x: source.x,
        y: source.y,
      };
      return diagonal({
        source: o,
        target: o,
      });
    })
    .remove();

  // Stash the old positions for transition.
  nodes.forEach(function (d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update(d);
}

//Redraw for zoom
function redraw() {
  //console.log("here", d3.event.translate, d3.event.scale);
  svg.attr(
    'transform',
    'translate(' + d3.event.translate + ')' + ' scale(' + d3.event.scale + ')'
  );
}
