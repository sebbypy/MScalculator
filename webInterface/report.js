
console.log("hello world")

async function genPDF(){

	lang = getCurrentLanguage()
	
	function addHeaderImage(base64Image){
		doc.addImage(base64,"JPEG",20,10,100,25)
	}

	function addGenerationDate(){
		doc.setFontSize(8);
		doc.text(translations['pdf_generated_on'][lang]+' '+getDateString(),150,290)
	}
	
	// Default export is a4 paper, portrait, using millimeters for units
	const doc = new jsPDF('a4');

	doc.setFontSize(15);
    
	
	var base64 = await getBase64FromUrl('https://images.prismic.io/bbri/0f1c879e-8d5e-4201-a0d2-2dbf3bd95d33_Buildwise_Horizontaal_noir_marge.png?auto=compress')
	//aspect ratio: 4:1
	addHeaderImage(base64)

	latestY = 35

	doc.text(translations['pdf_title'][lang], 20, latestY+20);

	doc.setFontSize(12);

	layers = getLayersInfo();
	bcs = getBoundaryConditions();


	RLayers = parseFloat(document.getElementById('R4').innerHTML).toFixed(2);
	Rtot = parseFloat(document.getElementById('R3').innerHTML).toFixed(2);
    deltaR = parseFloat(Rtot)-parseFloat(getTheoriticalR(true));

	bridgedLayer = getBridgedLayer();


	layers.forEach( (x,index) => {
	  if (!isAirLayer(x['material'])){
			x['resistance']=(x['thickness']/100/x['lambda']).toFixed(2); 
		}
		else{
			x['resistance']=getAirLayerResistance(x['material']).toFixed(2);
			}
		x['index']=index+1;

	});

	layers.forEach( (x,index) => {
		
		if (!isAirLayer(x['material'])){
	  
			x['resistance2']=(x['thickness']/100/x['lambda']).toFixed(2); 
			}
		else{
			x['resistance2']=getAirLayerResistance(x['material']).toFixed(2);
			}
	
		x['index']=index+1;

		if (x['index'] == bridgedLayer){
			
			x['resistance2'] = (parseFloat(x['resistance2']) + deltaR).toFixed(2);
		}
		x['materialName']=getMaterialName(x['material']);
		});
	
	
	layers.push({'thickness':getCumThickness(),'resistance':getTheoriticalR(),'resistance2':RLayers,'materialName':'Total paroi'});
	
	Rsup = 1/bcs['hi']+1/bcs['he'];
	
	//layers.push({'thickness':'','resistance':Rsup,'resistance2':Rsup,'materialName':'Rsi+Rse'});
	//layers.push({'thickness':'','resistance':getTheoriticalR(true),'resistance2':Rtot,'materialName':'Total(avec Rsi et Rse)'});

	
	headers = [ { header: translations['material_type'][lang], dataKey:'materialName'},
	            { header: translations['thickness_cm'][lang], dataKey: 'thickness' },
				{ header: translations['pdf_lambda'][lang], dataKey: 'lambda' },
				{ header: translations['pdf_R_bridged'][lang], dataKey: 'resistance2' },
				{ header: translations['pdf_R_unbridged'][lang], dataKey: 'resistance' }
				]

	// Couches
	doc.text(translations['pdf_layers_title'][lang],20,latestY+30)
	doc.setFontSize(8);
	doc.text(translations['pdf_layers_grey_line'][lang],20,latestY+35)
	doc.setFontSize(12);

	BWfillColor = [0,191,182];

	doc.autoTable( {startY: latestY+40,
					margin: {top:0,left:20},
					body:layers,
					columns:headers,
					styles: {
						halign: 'center',
						cellWidth: 30
					},
					theme: 'grid',
					headStyles:{
						fillColor: BWfillColor
					},
					columnStyles:{
					 0: {cellWidth:40},
					 2: {cellWidth:35},
					 3: {cellWidth:35},
					 4: {cellWidth:35},
					},
					didParseCell: function (data) {
					  if (data.row.index === bridgedLayer-1) {
						data.cell.styles.fillColor = [220, 220, 220]
					  }
					}
					});

	let previousTableY = doc.previousAutoTable.finalY; 

	headers = [ { header: '', dataKey:'materialName'},
				{ header: translations['pdf_withThermalBridge'][lang], dataKey: 'resistance2' },
				{ header: translations['pdf_withoutThermalBridge'][lang], dataKey: 'resistance' }
				]


	summary=[]
	summary.push({'resistance':getTheoriticalR(false),'resistance2':RLayers,'materialName':translations['pdf_r_wall'][lang]+' [m²K/W]'});
	summary.push({'resistance':Rsup,'resistance2':Rsup,'materialName':'Rsi+Rse [m²K/W]'});
	summary.push({'resistance':getTheoriticalR(true),'resistance2':Rtot,'materialName':translations['pdf_r_total'][lang]+' [m²K/W]'});
	summary.push({'resistance':(1/getTheoriticalR(true)).toFixed(3),'resistance2':(1/Rtot).toFixed(3),'materialName':'U [W/m²K]'});


	doc.text(translations['pdf_total_u_and_r'][lang],20,previousTableY+10)
	doc.autoTable( {startY: previousTableY+15,
					margin: {top:0,left:20},
					body:summary,
					columns:headers,
					styles: {
						halign: 'center',
						cellWidth: 30
					},
					theme: 'grid',
					headStyles:{
						fillColor: BWfillColor
					},
					columnStyles:{
					 0: {cellWidth:40},
					 2: {cellWidth:35},
					 3: {cellWidth:35},
					},
					});


	previousTableY = doc.previousAutoTable.finalY;

	// Profile metallique
	metalData = getMetalData();
    
    if (metalData['shape'] == 'C-shape'){
        metalData['shape']='0°'
    }
    if (metalData['shape'] == 'U-shape'){
        metalData['shape']='90°'
    }
    
	headers = [ {header: translations['profile_distance_from_inside_cm'][lang], dataKey:'p'},
	            {header: translations['profile_thickness_mm'][lang], dataKey: 'e' },
				{ header: translations['profile_width_cm'][lang], dataKey: 'w' },
				{ header: translations['profile_height_cm'][lang], dataKey: 'h' },
				{ header: translations['orientation'][lang], dataKey: 'shape' },
				]

	doc.text(translations['pdf_metal_profile_characteristics'][lang],20,previousTableY+10)
	doc.autoTable({	startY: previousTableY+15,
					margin: {top:0,left:20},
					body: [metalData],
					columns:headers,
					styles: {
						halign: 'center',
						cellWidth: 30
					},
					theme: 'grid',
					headStyles:{
						fillColor: BWfillColor
					},
					columnStyles:{
					 0: {cellWidth:45}
					}
	
					});


	bcs = getBoundaryConditions();
	headers = [ {header: 'hi [W/m²K]', dataKey:'hi'},
	            {header: 'he [W/m²K]', dataKey: 'he' },
				{ header: 'Ti [°C]', dataKey: 'Ti' },
				{ header: 'Te [°C]', dataKey: 'Te' },
				]

	previousTableY = doc.previousAutoTable.finalY; 
	doc.text(translations['boundary_conditions'][lang],20,previousTableY+10)
	doc.autoTable({	startY: previousTableY+15,
					margin: {top:0,left:20},
					body: [bcs],
					columns:headers,
					styles: {
						halign: 'center',
						cellWidth: 30
					},
					theme: 'grid',
					headStyles:{	
						fillColor: BWfillColor
						},
					});

	
	previousTableY = doc.previousAutoTable.finalY; 

	addGenerationDate();
	
	
	doc.addPage()

	addHeaderImage(base64)

	latestY = 25

	doc.setFontSize(15);

	doc.text(translations['pdf_title'][lang], 20, latestY+20);

	doc.setFontSize(12);
	doc.text(translations['pdf_drawing_and_temperature_field'][lang],20,latestY+30);

	await addPlotlyImage(doc,'geometryPlot',20,70);
	await addPlotlyImage(doc,'temperaturePlot',100,70);

	addGenerationDate()

	window.open(URL.createObjectURL(doc.output("blob")))
}



