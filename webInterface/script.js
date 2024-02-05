
function addRow(eValue = 2, lambdaValue = 0.2, cValue = "insulation",checked='') {
	var table = document.getElementById( 'layersTable' );
	var nRows = table.rows.length;
	row = table.insertRow(-1);
	//cell0 = row.insertCell(0);
	cell1 = row.insertCell(0);
	cell2 = row.insertCell(1);
	cell3 = row.insertCell(2);
	cell4 = row.insertCell(3);
	
	cell5 = row.insertCell(4);
	
	cell1.innerHTML='<input type="number" min="0" id="e'+nRows.toString()+'"size="6" value="'+eValue.toString()+'" onchange="drawAll();return null;"/>'
	cell2.innerHTML='<input type="number" min="0.010" id="t'+nRows.toString()+'" size="8" step="0.001" value="'+lambdaValue.toString()+'"/>'
	cell3.innerHTML='<select id="m'+nRows.toString()+'" onchange="changeType('+nRows.toString()+')"</select>'
	
	var select = document.getElementById('m'+nRows.toString());
    var options = getMaterials();

    for(var i = 0; i < options.length; i++) {
        var opt = options[i];
        var el = document.createElement("option");
        el.textContent = getMaterialName(opt);
        el.value = opt;
		el.setAttribute('lang_key',opt);
        select.appendChild(el);
    }
	
	
	cell4.innerHTML='<input type="checkbox" id="cb'+nRows.toString()+'" onchange="cbselected('+nRows.toString()+');" '+checked+'/>'
	cell4.classList.add("rightalign")

	let upbtn =  document.createElement("button");
	upbtn.id = "up"+nRows.toString();
	//upbtn.innerHTML = "&uarr;"; // arrow up
    //upbtn.innerHTML = "<i
    upbtn.innerHTML ='<i class="arrow up"></i>'
	upbtn.onclick = function(){upNdown(nRows,'up');}
    
	cell5.appendChild(upbtn);
	
	let downbtn =  document.createElement("button");
	downbtn.id = "down"+nRows.toString();
    downbtn.innerHTML ='<i class="arrow down"></i>'
	downbtn.onclick = function(){upNdown(nRows,'down');}
	
	cell5.appendChild(downbtn);

	/*let delbtn =  document.createElement("button");
	delbtn.id = "del"+nRows.toString();
	delbtn.innerHTML = "&#10008;"; //cross
	cell5.appendChild(delbtn);
	*/	
	select = document.getElementById( "m"+nRows.toString());
	select.value=cValue,
	drawAll();
}


function removeRow() {
	var table = document.getElementById( 'layersTable' );
	table.deleteRow(-1);
	drawAll();
}


function upNdown(index,direction)
{


	var rows = document.getElementById("layersTable").rows,
	parent = rows[index].parentNode;
	if(direction === "up")
	{
		 if(index > 1){
			parent.insertBefore(rows[index],rows[index - 1]);
			// when the row go up the index will be equal to index - 1
			switchElementsIds(index,index-1);
			index--;
		}
	 }
	 
	 if(direction === "down")
	 {
		 if(index < rows.length -1){
			parent.insertBefore(rows[index + 1],rows[index]);
			// when the row go down the index will be equal to index + 1
			switchElementsIds(index,index+1);
			index++;
			
		}
	 }
	 drawAll();
}

function switchElementsIds(rowid1,rowid2){
	
	var typeID = ["e","t","m","cb","up","down"];
	
	
	
	typeID.forEach( item => {
		
		var id1 = item+rowid1.toString();
		var id2 = item+rowid2.toString();
		
		element1 = document.getElementById(id1);
		element2 = document.getElementById(id2);

		element1.id = id2;
		element2.id = id1;
		
		if (item=='m'){
			element1.onchange = function() {changeType(rowid2);}
			element2.onchange = function() {changeType(rowid1);}
		}
		if (item=="cb"){
			element1.onchange = function() {cbselected(rowid2);}
			element2.onchange = function() {cbselected(rowid1);}
		}
		if (item=='up'){
			element1.onclick = function() { upNdown(rowid2,'up')}
			element2.onclick = function() {upNdown(rowid1,'up');}
		}
		if (item=='down'){
			element1.onclick = function() { upNdown(rowid2,'down')}
			element2.onclick = function() {upNdown(rowid1,'down');}
		}
	});
	
	
}



function cbselected(checkboxid) {
	var table = document.getElementById( 'layersTable' );
	var nRows = table.rows.length;
	
	for (let i=1; i<nRows; i+=1){
		var cb = document.getElementById('cb'+i.toString());
		
		if (checkboxid != i){
			cb.checked = false;
		}
		else{
			cb.checked = true; //this way, it remains true if try to unclick --> always one remains clicked
		}
	}

}


function getBridgedLayer(){

	var table = document.getElementById( 'layersTable' );
	var nRows = table.rows.length;
	
	for (let i=1; i<nRows; i+=1){
		var cb = document.getElementById('cb'+i.toString());
		
		if (cb.checked){
			return i;
		}
	}

}


// material functions

function getMaterials(){

    return ['gypsum','wood','insulation','briques','stone','concreteBlocs','air_nv','air_pv']
    
}

function getColors(){

	return {'gypsum':'White',
			'wood':'Brown',
			'insulation':'Yellow',
			'briques':'Indianred', //Coral is also good
			'air_pv':'lightblue',
			'air_nv':'lightblue',	
			'stone':'grey',
			'concreteBlocs':'grey'
			};
}

function getDefaultMaterialConductivity(material){

	var dict = {'gypsum': 0.2,
				'insulation':0.035,
				'briques':1.5,
				'wood':0.13,
				'stone':2.5,
				'concreteBlocs':1.5
				};
			
	return dict[material];

}


function getMaterialName(material){

	lang=getCurrentLanguage()
	
	
	
	var dict = {'gypsum':{
					'en':'Plaster',
					'fr':'Platre',
					'nl':'Pleister'
					},
				'insulation':{
					'en':'Insulation',
					'fr':'Isolant',
					'nl':'Insulatie'
					},
				'briques':{
					'en':'Bricks',
					'fr':'Briques',
					'nl':'Pleister'
					},
				'wood':{
					'en':'Wood',
					'fr':'Bois',
					'nl':'Hout'
					},
				'air_nv':{
					'en':'Air (not ventilated)',
					'fr':'Lame d\'air NV (R=0.18)',
					'nl':'Lucht (zonder circulatie)'
					},
				'air_pv':{
					'en':'Air (ventilated)',
					'fr':'Lame d\'air PV (R=0.09)',
					'nl':'Lucht (met circulatie)'
					},
				'stone':{
					'en':'Stone',
					'fr':'Pierre',
					'nl':'Pierre'
					},
				'concreteBlocs':{
					'en':'Concrete',
					'fr':'Blocs béton',
					'nl':'Betonblok'
					}
				};
			
	return translations[material][lang];

	//return dict[material][lang];

}

function isAirLayer(material){

	var airLayersTypes=['air_nv','air_pv'];

	if (airLayersTypes.includes(material))
	{
		return true;
	}
	else{
		return false;
	}
}

function hasMoreThanOneAirLayer(){

	layers=getLayersInfo()
	
	var nAirLayers = 0;
	
	layers.forEach(item =>{
		material = item['material'];
		
		if (isAirLayer(material)){
			nAirLayers += 1;
		}	
	});
	
	if (nAirLayers > 1){
		return true
		}
	else{
		return false
		}
}




function getAirLayerResistance(material){

	var dict = {'air_nv':0.18,
				'air_pv':0.09
				};
				
	return dict[material]
}



function changeType(layerid){
	lang = getCurrentLanguage();

	if (hasMoreThanOneAirLayer()){
		alert(translations['air_layers_warning'][lang]);
	}

	var layers = getLayersInfo();
	var counter=1;
	layers.forEach(item => {
		colorElement = document.getElementById('m'+counter.toString());
		lambdaElement = document.getElementById('t'+counter.toString());
	
		material = item['material']
		
		if (layerid == counter && isAirLayer(material) ){
			//colorElement.value = 'air';
			lambdaElement.value = NaN;
			//colorElement.disabled = true;
			lambdaElement.disabled = true;
			
			}
		else {
			if (layerid != counter && isAirLayer(material) ){
				//colorElement.value = 'insulation'
				//colorElement.value = 'insulation'
				//colorElement.disabled = false;
				lambdaElement.disabled = false;
				//lambdaElement.value = '0.035';
			
			}
			if (layerid == counter && !isAirLayer(material)){

			   	//colorElement.disabled = false;
				lambdaElement.disabled = false;
				//colorElement.value = 'insulation';
				lambdaElement.value = getDefaultMaterialConductivity(item['material']);
			
			}
		}
		
		
		counter+=1
	}
	);
	drawAll()
}


function getLayersInfo(){
	var table = document.getElementById( 'layersTable' );
	var nRows = table.rows.length;

	var layers = [];

	for (let i=1; i<nRows; i+=1){
		//var type = document.getElementById('type'+i.toString()).value
		var thickness = document.getElementById('e'+i.toString()).value
		var kappa     = document.getElementById('t'+i.toString()).value
		var material  = document.getElementById('m'+i.toString()).value

		//console.log(thickness,kappa,material)
		
		var layerJson = {};
		//layerJson['type']= type;
		layerJson['thickness']=thickness;
		layerJson['lambda']=kappa;
		layerJson['material']=material;
		
		layers.push(layerJson);

	}
	return layers;
}

function getCumThickness(){
	var layers = getLayersInfo();
	
	var cumT = 0;
	
	layers.forEach(item => {cumT += parseFloat(item['thickness']) } );

	return cumT
}

function getTheoriticalR(withRsiRse=false){
	var layers = getLayersInfo();
	var cumR = 0;
	
	layers.forEach(item => {
	if (isAirLayer(item['material'])){
		cumR += getAirLayerResistance(item['material']);
		}
	else{
		cumR += parseFloat(item['thickness'])/100/parseFloat(item['lambda']); 
		}
	} 
	);

	if (withRsiRse){
		bcs= getBoundaryConditions();
		cumR+= 1/bcs['hi']+1/bcs['he'];
	}
	return cumR.toFixed(2);
}


function getMetalData(){
	//var table = document.getElementById( 'metalTable' );

	var data = {'shape':document.getElementById('MSshape').value,
				'e':parseFloat(document.getElementById('MSe').value),
				'h':parseFloat(document.getElementById('MSh').value),
				'w':parseFloat(document.getElementById('MSw').value),
				'p':parseFloat(document.getElementById('MSp').value),
				'EA':parseFloat(document.getElementById('MSentreAxe').value)
				};
	//console.log(data);
	
	return data;		
}

function getBoundaryConditions(){

	var data = {'hi':parseFloat(document.getElementById('hi').value),
				'he':parseFloat(document.getElementById('he').value),
				'Te':parseFloat(document.getElementById('Te').value),
				'Ti':parseFloat(document.getElementById('Ti').value),
				};
				
	console.log(data);
	return data;
}




async function loadMSCalculator(){
	pyodide.runPython(await (await fetch('https://raw.githubusercontent.com/sebbypy/MScalculator/main/python/MSCalculator.py')).text());
}


async function loadAllPython(){

	await loadPyodide({
          indexURL : "https://cdn.jsdelivr.net/pyodide/v0.17.0/full/"
        });

	await pyodide.loadPackage('numpy');
	await loadMSCalculator();

}

async function computeAndPlot(){
	lang = getCurrentLanguage()
	
	if (hasMoreThanOneAirLayer()){
		alert(translations['air_layers_warning'][lang]);
		return
	}
	var dataToPlot = await compute();
	Xvalues = dataToPlot[0];
	Yvalues = dataToPlot[1];
	Zvalues = dataToPlot[2];
	Rvalues = dataToPlot[3];
	
	
	showRvalues(Rvalues);
	plotTemperatureField(Xvalues,Yvalues,Zvalues);

}

function showRvalues(Rvalues){

	document.getElementById("R1").innerHTML = '('+Rvalues.get('R1').toFixed(2)+')';
	document.getElementById("R2").innerHTML = '('+Rvalues.get('R2').toFixed(2)+')';
	document.getElementById("Rsup2").innerHTML = '('+(Rvalues.get('R1')-Rvalues.get('R2')).toFixed(2)+')';
	document.getElementById("Uvalue2").innerHTML = '('+(1/Rvalues.get('R1')).toFixed(3)+')';

	document.getElementById("R3").innerHTML = Rvalues.get('R3').toFixed(2);
	document.getElementById("R4").innerHTML = Rvalues.get('R4').toFixed(2);
	document.getElementById("Rsup").innerHTML = (Rvalues.get('R3')-Rvalues.get('R4')).toFixed(2);
	document.getElementById("Uvalue").innerHTML = (1/Rvalues.get('R3')).toFixed(3);
}


async function compute(){

	layers = getLayersInfo();
	metal = getMetalData();
	bcs = getBoundaryConditions();

	//pas parameters as string
	eIsol = [] 
	kIsol = []
	hMetal = metal['h']
	pMetal = metal['p']
	wMetal = metal['w']
	eMetal = metal['e']
	entreAxe = metal['EA']
	shape = metal['shape']

	bcs = getBoundaryConditions();

	layers.forEach(item => { eIsol.push(parseFloat(item['thickness'])) })
	layers.forEach(item => { kIsol.push(parseFloat(item['lambda'])) })


	airLayerResistance=0.18
	layers.forEach(item => { 
		if (isAirLayer(item['material']))
		{
			airLayerResistance = getAirLayerResistance(item['material']);
		}
	});
		
	await pyodide.runPython(`

import js
eIsol = [x/100 for x in js.eIsol.to_py()]
kIsol = js.kIsol.to_py()
eMetal = js.eMetal/1000 #mm in js, m in py
pMetal = js.pMetal/100  #cm to mm
hMetal = js.hMetal/100  
wMetal = js.wMetal/100
shape = js.shape;
entreAxe = js.entreAxe/100

ResistanceAirLayer = js.airLayerResistance

bcs = js.bcs.to_py()

solver = MsSolver(layersThickness = eIsol,
					layersConductivity = kIsol.copy() , 
					pMetal=pMetal , 
					wMetal = wMetal, 
					hMetal = hMetal, 
					entreAxe = entreAxe,
					kMetal = 50, 
					eMetal = eMetal, 
					hi=bcs['hi'],
					he=bcs['he'],
					Ti=bcs['Ti'],
					Te=bcs['Te'],                         
					MStype=shape,
					ResistanceAirLayer=ResistanceAirLayer
					)
					
solver.solve()
TemperatureField = solver.T
x,y = solver.getFlattenedXandY()
Rvalues = solver.computeUandRValues()

							
x=x*100 #back to cm
y=y*100 #back to cm
`)

	var X=pyodide.globals.get('x').toJs();
	var Y=pyodide.globals.get('y').toJs();
	var Z=pyodide.globals.get('TemperatureField').toJs();
	var Rvals=pyodide.globals.get('Rvalues').toJs();

	//console.log(Rvals);

	return [X,Y,Z,Rvals]
}


async function plotTemperatureField(Xvalues,Yvalues,Zvalues){

		metalData = getMetalData();
		var entreAxe = metalData['EA'];
		var cumThickness = getCumThickness();

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
		width: 400,
		height: 800,
		}

	metalData = getMetalDrawing();

	var metalTrace = {
		x: metalData[0],
		y: metalData[1],
		mode: 'lines',
		line: {
			color: 'Black',
			width: 2
		}
	}

	var contour = {
		x: Xvalues,
		y: Yvalues,
		z: Zvalues,
		type: 'contour',
		colorbar:{
			thickness: 50,
			thicknessmode: 'pixels'
			}
		}
		
	temperaturePlot = document.getElementById('temperaturePlot');
	Plotly.newPlot(temperaturePlot, [contour,metalTrace], layout);

}



function updateRsi(){
	hiElement = document.getElementById("hi")
	hiValue = hiElement.value
	RsiValue = 1/hiValue
	
	RSI = document.getElementById("RSIvalue")
	RSI.innerHTML=RsiValue.toFixed(2).toString()+')'
	
}
function updateRse(){
	heElement = document.getElementById("he")
	heValue = heElement.value
	RseValue = 1/heValue
	
	RSE = document.getElementById("RSEvalue")
	RSE.innerHTML=RseValue.toFixed(2).toString()+')'
	
}


const getBase64FromUrl = async (url) => {
  const data = await fetch(url);
  const blob = await data.blob();
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(blob); 
    reader.onloadend = () => {
      const base64data = reader.result;   
      resolve(base64data);
    }
  });
}

function getDateString(){
	var today = new Date();
	var dd = String(today.getDate()).padStart(2, '0');
	var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
	var yyyy = today.getFullYear();
	today = dd + '/' + mm+ '/' + yyyy;

	return today;
}

async function addPlotlyImage(doc,plotlyPlot,xpos,ypos) {
  
	geoplot = document.getElementById(plotlyPlot);
	await Plotly.toImage(plotlyPlot, { format: 'jpeg', width: 1350, height: 2700 })
		.then(
             function(url)
         {
			doc.addImage(url,"JPEG",xpos,ypos,75,150);
	    }
         );
  
}



