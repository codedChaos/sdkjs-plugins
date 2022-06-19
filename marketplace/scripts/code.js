/**
 *
 * (c) Copyright Ascensio System SIA 2020
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
(function(window, undefined) {

    window.Asc.plugin.init = function() {
		window.Asc.plugin.resizeWindow(550, 585, 450, 540, 0, 0);
		// none
    };

    window.Asc.plugin.button = function() {
		this.executeCommand("close", "");
    };

	window.addEventListener("message", function(message) {
		let data = JSON.parse(message.data);
			
		switch (data.type) {
			case 'getInstalled':
				window.Asc.plugin.executeMethod("GetInstalledPlugins", null, function(result) {
					message.source.postMessage(JSON.stringify({type: 'InstalledPlugins', data: result}), "*");
				});
				break;
			case 'install':
				window.Asc.plugin.executeMethod("InstallPlugin", [data.config], function(result) {
					setTimeout(function(){
						message.source.postMessage(JSON.stringify(result), "*");
					}, 100);
				});
				break;
			case 'remove':
				window.Asc.plugin.executeMethod("RemovePlugin", [data.guid], function(result) {
					setTimeout(function(){
						message.source.postMessage(JSON.stringify(result), "*");

					}, 100);
				});
				break;
			case 'update':
				window.Asc.plugin.executeMethod("UpdatePlugin", [data.config], function(result) {
					setTimeout(function(){
						message.source.postMessage(JSON.stringify(result), "*");
					}, 100);
				});
				break;
		}
		
	}, false);

	window.Asc.plugin.onThemeChanged = function(theme)
	{
		window.Asc.plugin.onThemeChangedBase(theme);
		let style = document.getElementsByTagName('head')[0].lastChild;
		let ifr = document.getElementById('iframe');
		if (ifr && ifr.contentWindow)
			ifr.contentWindow.postMessage(JSON.stringify({ type: 'Theme', theme: theme, style : style.innerHTML}));
	};

	let installed = [
		{
			url : "https://raw.githubusercontent.com/ONLYOFFICE/plugin-autocomplete/master/config.json",
			guid : "A103601F-FDA0-418A-BC37-A514031894C0",
			canRemoved : true,
			obj : {
					name: "example_autocomplete",
					guid: "asc.{A103601F-FDA0-418A-BC37-A514031894C0}",
					version: "1.0.0",
					variations: [
									{
										description: "example_autocomplete",
										url: "index.html",
										icons: ["resources/img/icon.png","resources/img/icon@2x.png"],
										isViewer: false,
										EditorsSupport: ["word","slide","cell"],
										isVisual: false,
										isModal: false,
										isInsideMode: false,
										isSystem: true,
										initDataType: "none",
										initData: "",
										isUpdateOleOnResize: false,
										buttons: [],
										events: ["onInputHelperClear","onInputHelperInput"]
									}
								]
				  }
		},
		{
			url : "https://raw.githubusercontent.com/ONLYOFFICE/plugin-macros/master/config.json",
			guid : "E6978D28-0441-4BD7-8346-82FAD68BCA3B",
			canRemoved : false,
			obj : {
					name: "Macros", 
					nameLocale: {
									ru: "Макросы",
									fr: "Macros",
									es: "Macros",
									de: "Makros"
								},
					guid: "asc.{E6978D28-0441-4BD7-8346-82FAD68BCA3B}",
					version: "1.0.0",
					group: {
								name: "Macros",
								rank: 2
						   },
					variations: [
									{
										description: "Macros",
										descriptionLocale: {
																ru: "Макросы",
																fr: "Macros",
																es: "Macros",
																de:"Makros"
														   },
										url: "index.html",
										help: "https://api.onlyoffice.com/plugin/macros",
										icons: ["resources/light/icon.png","resources/light/icon@2x.png"],
										icons2: [
													{
														style: "light",
														"100%": {
																	normal: "resources/light/icon.png"
																},
														"125%": {
																	normal: "resources/light/icon@1.25x.png"
																},
														"150%": {
																	normal: "resources/light/icon@1.5x.png"
																},
														"175%": {
																	normal: "resources/light/icon@1.75x.png"
																},
														"200%": {
																	normal:"resources/light/icon@2x.png"
																}
													},
													{
														style: "dark", 
														"100%": {
																	normal:"resources/dark/icon.png"
																},
														"125%": {
																	normal: "resources/dark/icon@1.25x.png"
																},
														"150%": {
																	normal: "resources/dark/icon@1.5x.png"
																},
														"175%": {
																	normal: "resources/dark/icon@1.75x.png"
																},
														"200%": {
																	normal: "resources/dark/icon@2x.png"
																}
													}
												],
										isViewer: false,
										EditorsSupport: ["word","cell","slide"],
										isVisual: true,
										isModal: true,
										isInsideMode: false,
										initDataType: "",
										initData: "",
										isUpdateOleOnResize: false,
										buttons: [
													{
														text: "Ok",
														primary: true
													},
													{
														text: "Cancel",
														primary: false,
														textLocale: {
																		ru:"Отмена",
																		fr:"Annuler",
																		es:"Cancelar",
																		de:"Abbrechen"
																	}
													}
												 ]
									}
								]
				}
		},
		{
			url : "https://raw.githubusercontent.com/ONLYOFFICE/plugin-mendeley/master/config.json",
			guid : "BE5CBF95-C0AD-4842-B157-AC40FEDD9441",
			canRemoved : true,
			obj : {
					name: "Mendeley",
					guid: "asc.{BE5CBF95-C0AD-4842-B157-AC40FEDD9441}",
					version: "1.0.0",
					variations: [
									{
										description: "Mendeley",
										url: "index.html",
										icons: ["resources/light/icon.png","resources/light/icon@2x.png"],
										icons2: [
													{
														style: "light",
														"100%": {
																	normal:"resources/light/icon.png"
																},
														"125%": {
																	normal: "resources/light/icon@1.25x.png"
																},
														"150%": {
																	normal:"resources/light/icon@1.5x.png"
																},
														"175%": {
																	normal: "resources/light/icon@1.75x.png"
																},
														"200%": {
																	normal: "resources/light/icon@2x.png"
																}
													},
													{
														style: "dark",
														"100%": {
																	normal: "resources/dark/icon.png"
																},
														"125%": {
																	normal: "resources/dark/icon@1.25x.png"
																},
														"150%": {
																	normal: "resources/dark/icon@1.5x.png"
																},
														"175%": {
																	normal: "resources/dark/icon@1.75x.png"
																},
														"200%": {
																	normal: "resources/dark/icon@2x.png"
																}
													}
												],
										isViewer: false,
										EditorsSupport: ["word"],
										initDataType: "text",
										initData: "",
										isVisual: true,
										isModal: false,
										isInsideMode: true,
										isUpdateOleOnResize: false,
										initOnSelectionChanged: false
									}
								]
				}
		},
		{
			url : "https://raw.githubusercontent.com/ONLYOFFICE/plugin-deepl/master/config.json",
			guid : "b78a062b-e349-4634-8a44-99825600d299",
			canRemoved : true,
			obj : {
					name: "DeepL",
					nameLocale: {
						ru: "DeepL",
						fr: "DeepL",
						es: "DeepL",
						de: "DeepL"
					},
					guid: "asc.{b78a062b-e349-4634-8a44-99825600d299}",
					version: "1.0.0",
				
					variations: [
						{
							description: "Translator",
							descriptionLocale: {
								"ru": "DeepL",
								"fr": "DeepL",
								"es": "DeepL",
								"de": "DeepL"
							},
							url: "index.html",
				
							icons: [ "resources/light/icon.png", "resources/light/icon@2x.png" ],
							icons2: [
								{
									theme : "flat",
									style : "light",
									
									"100%": {
										normal: "resources/light/icon.png"
									},
									"125%": {
										normal: "resources/light/icon@1.25x.png"
									},
									"150%": {
										normal: "resources/light/icon@1.5x.png"
									},
									"175%": {
										normal: "resources/light/icon@1.75x.png"
									},
									"200%": {
										normal: "resources/light/icon@2x.png"
									},
									default: {
										normal: "resources/light/icon.png"
									}
								},
								{
									theme : "flatDark",
									style : "dark",
									
									"100%": {
										normal: "resources/dark/icon.png"
									},
									"125%": {
										normal: "resources/dark/icon@1.25x.png"
									},
									"150%": {
										normal: "resources/dark/icon@1.5x.png"
									},
									"175%": {
										normal: "resources/dark/icon@1.75x.png"
									},
									"200%": {
										normal: "resources/dark/icon@2x.png"
									}
								}
							],
							isViewer: true,
							EditorsSupport: [ "word", "slide", "cell" ],
							isVisual: true,
							isModal: false,
							isInsideMode: true,
							initDataType: "text",
							initData: "",
							isUpdateOleOnResize: false,
							buttons: [],
							initOnSelectionChanged: true
						}
					]
				}
		}
	];

})(window, undefined);
