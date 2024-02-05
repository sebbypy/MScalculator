function drawAll(){

	entreAxe = getMetalData()['EA'];
	layerShapes = getLayersShape(entreAxe);
	
	cumThickness=getCumThickness();
	metalData = getMetalDrawing();

	var layout = {
		margin: {
		l: 30,
		r: 10,
		b: 30,
		t: 10,
	  },
		paper_bgcolor:"Aliceblue",
		plot_bgcolor:"Aliceblue",

		xaxis: {
			range: [-1,cumThickness],
			showgrid: false,
			zeroline: false,
			showline: false,
			autotick: true,
			tickmode: "array",
			tickvals: [0,cumThickness],
		  },
		yaxis: {
			range: [-1,entreAxe],
			scaleanchor: "x",
			scaleratio: 1,
			showgrid: false,
			zeroline: true,
			showline: false,
			autotick: true,
			tickmode: "array",
			tickvals: [0,entreAxe],
		},
		width: 300,
		height: 800,
		shapes: layerShapes
	};

	var metalTrace = {
		x: metalData[0],
		y: metalData[1],
		mode: 'lines',
		line: {
			color: 'Red',
			width: 4
		}
	}
	
	geometryPlot = document.getElementById('geometryPlot');
	Plotly.newPlot(geometryPlot, [metalTrace], layout );
}

function getLayersShape(entreAxe=60){

	var layers = getLayersInfo();
	var rectangleShapes = []

	var cumThickness = 0
	var endThickness = 0

	colors = getColors();

	layers.forEach(item => {

		endThickness = cumThickness+parseInt(item['thickness'],10)

		//Filled Rectangle
		var rect = {
			type: 'rect',
			x0: cumThickness,
			y0: 0,
			x1: endThickness,
			y1: entreAxe,
			line: {
				color: 'rgba(0, 0,0, 1)',
				width: 2
			},
			fillcolor: colors[item['material']],
			layer: 'below'
		};
		rectangleShapes.push(rect);
		
		if (item['material']==='briques')
		{
			brickShapes = getBrickShapes(cumThickness,item['thickness'],entreAxe)
			rectangleShapes = rectangleShapes.concat(brickShapes)
		}
		if (item['material']==='stone')
		{
			patterns = getStoneShapes(cumThickness,item['thickness'],entreAxe)
			rectangleShapes = rectangleShapes.concat(patterns)
		}
		if (item['material']==='concreteBlocs')
		{
			patterns = getBlockShape(cumThickness,item['thickness'],entreAxe)
			rectangleShapes = rectangleShapes.concat(patterns)
		}

		cumThickness = endThickness;
		
	}
	);

	return rectangleShapes;

}

function getBlockShape(startX,width,height,refHeight=20){

    bricksShapes = []

	var nBrickRows = Math.floor(height/refHeight);
	var brickHeight = height/nBrickRows
	var brickWidth =  Math.floor(width) //convert to int
	
	
	for (let i=0; i<nBrickRows; i+=1){
		
		var rect1 = {
			type: 'rect',
			x0: startX,
			y0: i*brickHeight,
			x1: startX+brickWidth,
			y1: (i+1)*brickHeight,
			line: {
				color: 'rgba(0,0,1, 1)',
				width: 2
			},
			layer: 'above'
		};
		
		bricksShapes.push(rect1);
		
	}
	console.log(bricksShapes)
	return bricksShapes;
}


function getStoneShapes(startX,width,height){

	return getBrickShapes(startX,width,height,14,'beige','4')
}

function getBrickShapes(startX,width,height,refHeight=7,color='black',w=2){

	bricksShapes = []

	var nBrickRows = Math.floor(height/refHeight);
	var brickHeight = height/nBrickRows
	var brickWidth =  bricklen = width/1.5
	
	for (let i=0; i<nBrickRows; i+=1){

		rowStart = startX
		
		start1=startX
		if (i%2==0){
			width1=brickWidth
			width2=brickWidth/2
			}
		else{
			width1=brickWidth/2
			width2=brickWidth
		}
		start2=start1+width1

		
		var rect1 = {
			type: 'rect',
			x0: start1,
			y0: i*brickHeight,
			x1: start1+width1,
			y1: (i+1)*brickHeight,
			line: {
				color: color,
				width: w
			},
			layer: 'below'
		};
		
		var rect2 = {
			type: 'rect',
			x0: start2,
			y0: i*brickHeight,
			x1: start2+width2,
			y1: (i+1)*brickHeight,
			line: {
				color: color,
				width: w
			},
			layer: 'below'
		};
		
		bricksShapes.push(rect1);
		bricksShapes.push(rect2);
		
	}
	return bricksShapes;
	
}
	


function getMetalDrawing(){

	metalData = getMetalData();

	if (metalData['shape'] == 'C-shape'){

		ystart = metalData['EA']/2 - metalData['h']/2;
		x1 = metalData['p'];
		y1 = ystart;
		x2 = x1;
		y2 = y1+metalData['h'];
		x3 = x1+metalData['w'];
		y3=y2
		y4=y1
		x4=x3
	}
	if (metalData['shape'] == 'U-shape'){

		ystart = metalData['EA']/2  + metalData['w']/2;

		x1 = metalData['p'] + metalData['h'];
		y1 = ystart;

		x2 = x1 - metalData['h'];
		y2 = y1;

		x3 = x2;
		y3 = y2 - metalData['w']

		x4=x1
		y4=y3
	}
	//console.log(x1)
	
	x=[x1,x2,x3,x4];
	y=[y1,y2,y3,y4];
	
	return  [x,y]
}


