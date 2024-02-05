
const translations = {
  "title": {
    "en": "U-value calculator with metal profiles",
    "fr": "Calculateur de valeurs U avec profilés métalliques",
    "nl": "U-waarde calculator met metal profielen"
  },
  "insert_layers":  {
    "en": "Insert all layers",
    "fr": "Insérer les couches",
    "nl": "Voer in de layers"
  },
  "thickness_cm":{
    "en": "Thickness [cm]",
    "fr": "Epaisseur [cm]",
    "nl": "Dikte [cm]"
  },
   "insert_profile":  {
    "en": "Metal profile characteristics",
    "fr": "Caractéristiques du profilé",
    "nl": "Metalprofiel karakteristieken"
  },
  "orientation":{
	"en":"Orientation",
	"fr":"Orientation",
	"nl":"Orientatie"
	},
   "profile_width_cm":{
    "en": "Profile width [cm]",
    "fr": "Largeur du profilé [cm]",
    "nl": "Profiel breedte [cm]"
  },
   "boundary_conditions":{
    "en": "Boundary conditions",
    "fr": "Conditions aux limites",
    "nl": "Randvoorwaarden"
  },
  "profile_height_cm":{
    "en": "Profile height [cm]",
    "fr": "Hauteur du profilé [cm]",
    "nl": "Profiel hoogte [cm]"
  },
  "profile_thickness_mm":{
    "en": "Profile thickness [mm]",
    "fr": "Epaisseur du profilé [mm]",
    "nl": "Profiel dikte [mm]"
  },
  "profile_distance_from_inside_cm":{
    "en": "Profile position (distance from inside) [cm]",
    "fr": "Position du profilé (distance depuis l'intérieur) [cm]",
    "nl": "Profiel locatie (afstand vanaf binnenkant) [cm]"
  },
  "center_distance_cm":{
    "en": "Center distance [cm]",
    "fr": "Entre-axe [cm]",
    "nl": "Midden afstand [cm]"
  },
  "results":{
    "en": "Results",
    "fr": "Résultats",
    "nl": "Resultaten"
  },
  "material_type":{
    "en": "Material type",
    "fr": "Type de matériau",
    "nl": "Materiaaltype"
  },
  "associate_bridge_to_this_layer":{
    "en": "Apply thermal bridge to this layer",
    "fr": "Associer le pont thermique\n à cette couche",
    "nl": "Koudebrug aan dit leeg toepassen"
  },
  "with_profile":{
    "en": "With profile",
	"fr": "Avec profil",
	"nl": "Met profiel"
	},
   "without_profile":{
    "en": "(theoritical without profile)",
	"fr": "(theorique sans profil)",
	"nl": "(thoretische zonder profiel)"
	},
	"calculate_button":{
    "en": "Calculate",
	"fr": "Calculer",
	"nl": "Berekenen"
	},
	"generate_pdf":{
    "en": "Generate PDF report",
	"fr": "Générer rapport PDF",
	"nl": "PDF"
	},
	"add_layer":{
    "en": "Add layer",
	"fr": "Ajouter une couche",
	"nl": "Leeg toevoegen"
	},
	"delete_layer":{
    "en": "Delete layer",
	"fr": "Supprimer une couche",
	"nl": "Leeg verwijderen"
	},
	'gypsum':{
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
		},
	'pdf_title':{
		'en':'U calculator',
		'fr':'Calculateur U',
		'nl':'U rekenmachine'
		},
	'pdf_layers_title':{
		'en':'Descrition of the layers (inside to outside)',
		'fr':"Description des couches (de l'intérieur vers l'extérieur)",
		'nl':"Bescrhrijving van legen (van binnen naar buiten)"
		},
	'pdf_layers_grey_line':{
		'en':'The grey line is the one to which the thermal bridge has been applied',
		'fr':"La ligne grisée est celle à laquelle le pont thermique a été appliqué",
		'nl':"De grijze lijn is digene waarover de koudebrug toegepast werd"
	},
	'pdf_lambda':{
		'en':'Thermal conductivity [W/mK]',
		'fr':'Conductivité thermique [W/mK]',
		'nl':'Thermische conductiviteit [W/mK]'
		},
	'pdf_R_bridged':{
		'en':'R with thermal bridge [m²/KW]',
		'nl':'R met koudebrug [m²/KW]',
		'fr':'R avec pont thermique [m²/KW]'
	},
	'pdf_R_unbridged':{
		'en':'Theoritical R [m²/KW]',
		'nl':'Theoretische R [m²/KW]',
		'fr':'R théorique [m²/KW]'
	},
	'pdf_withThermalBridge':{
		'en':'With thermal bridge',
		'nl':'Met koudebrug',
		'fr':'Avec pont thermique'
		},
	'pdf_withoutThermalBridge':{
		'en':'Without thermal bridge',
		'nl':'Zonder koudebrug',
		'fr':'Sans pont thermique'
		},
	'pdf_drawing_and_temperature_field':{
		'en': 'Wall composition and temperature field',
		'nl': 'Wand samenstelling en temperatuur distributie',
		'fr': 'Composition de la paroi et champ de température'
		},
	'pdf_metal_profile_characteristics':{
		'en': 'characteristics of metal profile',
		'nl': 'Eigenschappen of metaal profiel',
		'fr': 'Caractéristiques de la structure métallique'},
	'pdf_total_u_and_r':{
		'en':'Total R and U values',
		'nl':'Totaal R en U waarden',
		'fr':'Valeurs U et R totales'
	},
	'pdf_r_wall':{
		'en':'R construction',
		'fr':'R paroi',
		'nl':'R wand'},
	'pdf_r_total':{
		'en':'Total R',
		'fr':'R Total',
		'nl':'Totaal R'
		},
	'pdf_generated_on':{
		'en':'Generated on',
		'fr':'Généré le',
		'nl':'Berekend op'
		},
	'air_layers_warning':{
		'en':'This tool can only compute with a single air layer. Please adapt you inputs in order to be able to launch the calculation',
		'fr':"Le calculateur ne peut traiter qu'une seule lame d'air. Modifiez la configuration pour pouvoir lancer le calcul",
		'nl':'Die tool kan maar 1 laag lucht handelen. Pas de configuratie aan om de berekening te kunnen uitvoeren'
		}	
};


function replaceTextBasedOnLanguage(currentLang) {
  document.querySelectorAll('[lang_key]').forEach(element => {
    const key = element.getAttribute('lang_key');
    // Check if the key exists in the translations and if the key has a translation for the current language
    if (translations[key] && translations[key][currentLang]) {
      const translation = translations[key][currentLang];

	  if (element.tagName == "INPUT"){
	    element.value = translation;
	  }
	  if (element.tagName == "SELECT"){
	    element.value = translation;
	  }
	  if (element.tagName == "OPTION"){
		element.textContent = translation;
	  }
			

      element.textContent = translation;
    } else {
      // If the translation for the key doesn't exist, you can either skip or set a default text
      console.warn(`No translation found for key: '${key}' in language: '${currentLang}'. Skipping...`);
      // Optional: Set a default text if necessary
      // element.textContent = "Translation not available";
    }
  });
}


document.getElementById('languageSelect').addEventListener('change', function() {
  const selectedLang = this.value;
  replaceTextBasedOnLanguage(selectedLang);
});

// Optional: Call on page load with default language
document.addEventListener('DOMContentLoaded', function() {
  const defaultLang = navigator.language.slice(0, 2); // Or your default language
  replaceTextBasedOnLanguage(defaultLang);
});


function getCurrentLanguage() {
  const languageSelect = document.getElementById('languageSelect');
  return languageSelect.value; // This will return the value of the selected option, e.g., 'en', 'fr', 'es', etc.
}
