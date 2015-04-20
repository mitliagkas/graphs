// We load the d3.js library from the Web.
require.config({paths: {d3: "http://d3js.org/d3.v3.min"}});
require(["d3"], function(d3) {
    // The code in this block is executed when the 
    // d3.js library has been loaded.
    
    // First, we specify the size of the canvas containing
    // the visualization (size of the <div> element).
    var width = 400,
        height = 400;

		var frogs = 10;

		// Linear color scale
		var color = d3.scale.linear()
					.domain([0, 20/Math.sqrt(frogs), 100/Math.sqrt(frogs)])
					.range(["green", "grey", "red"]);
    // We create a color scale.
    //var color = d3.scale.category20c();

    // We create a force-directed dynamic graph layout.
    var force = d3.layout.force()
        .charge(-150)
        .linkDistance(25)
        .linkStrength(0.5)
        .gravity(0.2)
        .theta(0.3)
        .size([width, height]);

    // In the <div> element, we create a <svg> graphic
    // that will contain our interactive visualization.
    var svg = d3.select("#d3-example").select("svg")
    if (svg.empty()) {
        svg = d3.select("#d3-example").append("svg")
                    .attr("width", width)
                    .attr("height", height);
    }
        
    // We load the JSON file.
    d3.json("rwgraph.json?nocache=" + (new Date()).getTime(), function(error, graph) {
        // In this block, the file has been loaded
        // and the 'graph' object contains our graph.
        
        // We load the nodes and links in the force-directed
        // graph.
        force.nodes(graph.nodes)
            .links(graph.links)
            .start();

				var nodes = force.nodes()
				nodes.forEach(function(o) { o.count=0; })

				var adjacency = graph.adjacency;

        // We create a <line> SVG element for each link
        // in the graph.
        var link = svg.selectAll(".link")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", function(d) { return 1; });
            //.style("stroke-width", function(d) { return 1+( (d.source.group != d.target.group) ? 1 : 0) });


        // We create a <circle> SVG element for each node
        // in the graph, and we specify a few attributes.
        var node = svg.selectAll(".node")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("class", "node")
						// radius
						.attr("r", 3) // .attr("r", function(d) { return Math.log(d.value+1)+3; })
            .style("fill", function(d) {
                // The node color depends on the club.
                return color(d.group); 
            });
            //.call(force.drag);
						
        // The name of each node is the node number.
        node.append("title")
            .text(function(d) { return d.name; });

				
        // We bind the positions of the SVG elements
        // to the positions of the dynamic force-directed graph,
        // at each time step.
        force.on("tick", function(e) {
					  // Push different nodes in different directions for clustering.
					 	var k = 6 * e.alpha;
						nodes.forEach(function(o, i) {
							o.x += o.group & 1 ? k : -k;
							o.y += o.group & 2 ? k : -k;
						});

            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });
        });


        d3.select("body").on("mousedown", function() {
						return
					  nodes.forEach(function(o, i) {
							    o.x += (Math.random() - .5) * 40;
									o.y += (Math.random() - .5) * 40;
						});
						force.resume();
				});

				svg.style("opacity", 1e-6)
						.transition()
						.duration(1000)
				    .style("opacity", 1);

		var delay = 300;
		//delayslider = d3.slider().axis(true).min(1).max(1000).value(200);
		//delayslider = d3.slider().value(200);
		
		var count = 0;

		//var step = 0;
		var nextcolor = 0;
		var madeprogressthisstep = false;

		// Initialize frogs position
		var frogvertex = []
		for (var i = 0; i < frogs; i++) {
			// Random
			// frogvertex[i] = ~~(Math.random() * nodes.length);
			// First node
			frogvertex[i] = 0;
		}
		
		window.setTimeout(function() {
					walk();
		}, 5000 + delay);

		window.setTimeout(function() {
					//force.stop()
					force.stop();
		}, 5000);

		// From:
		// https://gist.github.com/wrr/4750218

		function walk() {
			madeprogressthisstep = false;

			for (var i = 0; i < frogs; i++){
				//node[0][vertex].style.fill = color(7);
				node[0][frogvertex[i]].style.fill = color(nodes[frogvertex[i]].group);
			}

			for (var i = 0; i < frogs; i++){
				vertex = frogvertex[i];
				if (adjacency[vertex].length>0) {
					frogvertex[i] = adjacency[vertex][~~(Math.random() * adjacency[vertex].length)]['id'];
				}else{
					frogvertex[i] = ~~(Math.random() * nodes.length);
				}

				nodes[frogvertex[i]].count++;
				count++;

				//node[0][frogvertex[i]].style.fill = color(6);
				node[0][frogvertex[i]].setAttribute("r", 3+20*Math.sqrt(nodes[frogvertex[i]].count/count));
				if (!("group" in nodes[frogvertex[i]]) || nodes[frogvertex[i]].group == 0) {
					if (!madeprogressthisstep) {
						nextcolor++;
						madeprogressthisstep = true;
					}
					nodes[frogvertex[i]].group = nextcolor;
				}
			}

		  //var delay = delayslider.value()
			window.setTimeout(function() {
						walk();
			}, delay);
		}

		});


});








