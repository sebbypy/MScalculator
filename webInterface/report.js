
async function genPDF(){

	lang = getCurrentLanguage()
	
	function addHeaderImage(base64Image){
		doc.addImage(base64Image,"jpg",20,10,100,25)
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

	var logobase64 = "data:image/png;base64,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"
	doc.addImage(logobase64,"png",135,10,67,25)
	

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
	doc.addImage(logobase64,"png",135,10,67,25)


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



