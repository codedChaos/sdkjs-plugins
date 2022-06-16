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

// todo ссылки при install/update поправить
let allPlugins;                                          // list of all plugins from config
let installedPlugins;                                    // list of intalled plugins
const configUrl = './config.json';                       // url to config.json
const elements = {};                                     // all elements
const isDesctop = true;// window.AscDesktopEditor !== undefined; // desctop detecting
let isLoading = false;                                   // flag loading
let loader;                                              // loader
var Ps;                                                  // perfect scrollbar
const lang = detectLanguage() || "en-EN";                // current language
const shortLang = lang.split('-')[0];                     // short language
let bTranslate = false;                                  // flag translate or not
let translate =                                          // translations for current language
{
	"My plugins": "My plugins",
	"Marketplace": "Marketplace",
	"Submit your own plugin": "Submit your own plugin",
	"Install plugin manually": "Install plugin manually",
	"Install": "Install",
	"Remove": "Remove",
	"Update": "Update",
	"Offered by" : "Offered by",
	"Overview": "Overview",
	"Info & Support": "Info & Support",
	"Learn how to use": "Learn how to use",
	"the plugin in" : "the plugin in",
	"Contribute": "Contribute",
	"to the plugin developmen or report an issue on" : "to the plugin developmen or report an issue on",
	"Get help": "Get help",
	"with the plugin functionality on our forum." : "with the plugin functionality on our forum.",
	"Create a new plugin using" : "Create a new plugin using"
}
switch (shortLang) {
	case 'ru':
		translate["Loading"] = "Загрузка"
		break;
	case 'fr':
		translate["Loading"] = "Chargement"
		break;
	case 'es':
		translate["Loading"] = "Carga"
		break;
	case 'de':
		translate["Loading"] = "Laden"
		break;
	case 'cs':
		translate["Loading"] = "Načítání"
		break;
}
// for making preview
let counter = 0;
let row;
let theme;

// TODO решить проблему с темой и добавить для неё разные стили (после интеграции можно будет попробовать прокинуть событие смены темы)
// в теории её можно достать из parent.localStorage.getItem('ui-theme-id')
window.Asc = {
	plugin : {
		theme : {
			type :  JSON.parse(parent.localStorage.getItem('ui-theme')).type
		}
	}
}

// get translation file
getTranslation();
// fetch all plugins from config
fetchAllPlugins();
// get all installed plugins
setTimeout(function(){
	// для того, чтобы плагин успел запуститься и не слать кучу сообщений для временного решения
	sendMessage({type : 'getInstalled'}, '*');
}, 500);

window.onload = function() {
	// detect theme (this is not currently in use)
	theme = parent.localStorage.getItem('ui-theme-id') || '';
	console.log('detected theme: ' + theme);
	// init element
	initElemnts();

	if (shortLang == "en") {
		showMarketplace();
	}

	elements.btnMyPlugins.onclick = function() {
		// click on my plugins button
		if ( !this.classList.contains('btn_selected') ) {
			elements.btnMarketplace.classList.remove('btn_selected');
			this.classList.add('btn_selected');
			elements.linkNewPlugin.innerHTML = translate["Install plugin manually"];
			showListofPlugins(false);
		}
	};

	elements.btnMarketplace.onclick = function() {
		// click on marketplace button
		if ( !this.classList.contains('primary') ) {
			elements.btnMyPlugins.classList.remove('btn_selected');
			this.classList.add('btn_selected');
			elements.linkNewPlugin.innerHTML = translate["Submit your own plugin"];
			
			showListofPlugins(true);
		}
	};

	elements.arrow.onclick = function() {
		// click on left arrow in preview mode
		elements.divSelected.classList.add('hidden');
		elements.divSelectedMain.classList.add('hidden');
		elements.divBody.classList.remove('hidden');
		elements.arrow.classList.add('hidden');
		Ps.update();
	};

	elements.close.onclick = function() {
		// click on close button
		console.log('close window');
	};

	if (isLoading) {
		toogleLoader(true, "Loading");
	}
};

window.addEventListener('message', function(message) {
	// get message from editors
	message = JSON.parse(message.data);
	switch (message.type) {
		case 'InstalledPlugins':
			installedPlugins = message.data;
			if (allPlugins)
				getAllPluginsData();
			break;
		case 'Installed':
			installedPlugins.push(
				{
					url: allPlugins[message.guid].configUrl,
					guid: message.guid,
					canRemoved: true,
					obj: allPlugins[message.guid].config
				}
			);
			if (elements.btnMarketplace.classList.contains('btn_selected')) {
				let btn = this.document.getElementById(message.guid).lastChild.lastChild;
				btn.innerHTML = translate['Remove'];
				btn.onclick = function(e) {
					onClickRemove(e.target);
				};
			}
			if (!elements.divSelected.classList.contains('hidden')) {
				this.document.getElementById('btn_install').classList.add('hidden');
				this.document.getElementById('btn_remove').classList.remove('hidden');
			}
			toogleLoader(false);
			break;
		case 'Updated':
			let installed = installedPlugins.find(function(el) {
				return (el.guid == message.guid);
			});
			installed.obj.version = allPlugins[message.guid].config.version;
			if (!elements.divSelected.classList.contains('hidden')) {
				this.document.getElementById('btn_update').classList.add('hidden');
			}
			this.document.getElementById(message.guid).lastChild.firstChild.remove();
			toogleLoader(false);
			break;
		case 'Removed':
			// todo поправить для общего списка
			installedPlugins = installedPlugins.filter(function(el){return el.guid !== message.guid});
			if (elements.btnMyPlugins.classList.contains('btn_selected')) {
				showListofPlugins(false);
			} else {
				let btn = this.document.getElementById(message.guid).lastChild.lastChild;
				btn.innerHTML = translate['Install'];
				btn.onclick = function(e) {
					onClickInstall(e.target);
				};
				if (btn.parentNode.childElementCount > 1) {
					btn.parentNode.firstChild.remove();
				}
			}
			if (!elements.divSelected.classList.contains('hidden')) {
				this.document.getElementById('btn_remove').classList.add('hidden');
				this.document.getElementById('btn_install').classList.remove('hidden');
				this.document.getElementById('btn_update').classList.add('hidden');
			}
			toogleLoader(false);
			break;
		case 'Error':
			// TODO make error preview
			break;
	};
}, false);

function fetchAllPlugins() {
	// function for fetching all plugins from config
	makeRequest(configUrl).then(
		function(response) {
			allPlugins = JSON.parse(response);
			if (installedPlugins)
				getAllPluginsData();
		},
		function(err) {
			//TODO make error preview
			console.error(err);
			isLoading = false;
		}
	);
};

function makeRequest(url) {
	// this function makes GET request and return promise
	// maybe use fetch to in this function
	isLoading = true;
	return new Promise(function (resolve, reject) {
		let xhr = new XMLHttpRequest();
		xhr.open('GET', url, true);
		
		xhr.onload = function () {
			if (this.readyState == 4) {
				if (this.status == 200 || location.href.indexOf("file:") == 0) {
					setTimeout(() => {
						resolve(this.response);
					}, 500);
					// resolve(this.response);
				}
			}
		};

		xhr.onerror = function (err) {
			reject(err);
		};

		xhr.send(null);
	});
};

function sendMessage(message) {
	// this function sends message to editor
	parent.postMessage(JSON.stringify(message), '*');
};

function detectLanguage() {
	// TODO в теории язык можно вытащить из parent.location.search
	if (parent.location && parent.location.search) {
		let _langSearch = parent.location.search;
		let _pos1 = _langSearch.indexOf("lang=");
		let _pos2 = (-1 != _pos1) ? _langSearch.indexOf("&", _pos1) : -1;
		let _lang = null;
		if (_pos1 >= 0) {
			_pos1 += 5;

			if (_pos2 < 0)
				_pos2 = _langSearch.length;

			_lang = _langSearch.substr(_pos1, _pos2 - _pos1);
			if (_lang.length == 2) {
				_lang = (_lang.toLowerCase() + "-" + _lang.toUpperCase());
			}
		}
		return _lang;
	}
};

function initElemnts() {
	elements.btnMyPlugins = document.getElementById('btn_myPlugins');
	elements.btnMarketplace = document.getElementById('btn_marketplace');
	elements.linkNewPlugin = document.getElementById('link_newPlugin');
	elements.divBody = document.getElementById('div_body');
	elements.divMain = document.getElementById('div_main');
	elements.arrow = document.getElementById('arrow');
	elements.close = document.getElementById('close');
	elements.divHeader = document.getElementById('div_header');
	elements.divSelected = document.getElementById('div_selected_toolbar');
	elements.divSelectedMain = document.getElementById('div_selected_main');
	elements.imgIcon = document.getElementById('img_icon');
	elements.spanName = document.getElementById('span_name');
	elements.spanOffered = document.getElementById('span_offered');
	elements.btnUpdate = document.getElementById('btn_update');
	elements.btnRemove = document.getElementById('btn_remove');
	elements.btnInstall = document.getElementById('btn_install');
	elements.spanSelectedDescr = document.getElementById('span_selected_description');
	elements.imgScreenshot = document.getElementById('image_screenshot');
	elements.linkPlugin = document.getElementById('link_plugin');
};

function toogleLoader(show, text) {
	// show or hide loader
	if (!show) {
		document.getElementById('loader-container').classList.add('hidden');
		loader && (loader.remove ? loader.remove() : $('#loader-container')[0].removeChild(loader));
		loader = undefined;	
	} else if(!loader) {
		document.getElementById('loader-container').classList.remove('hidden');
		loader && (loader.remove ? loader.remove() : $('#loader-container')[0].removeChild(loader));
		loader = showLoader($('#loader-container')[0], (translate[text] || text) + '...');
	}
};

function getAllPluginsData() {
	let count = 0; 
	for (const guid in allPlugins) {
		count++;
		let pluginUrl = allPlugins[guid].configUrl;
		makeRequest(pluginUrl).then(
			function(response) {
				let config = JSON.parse(response);
				let guid = config.guid.substring(5, 41);
				allPlugins[guid].config = config;
				Ps.update();
				isLoading = false;
				count--;
				if (!count) {
					showListofPlugins(true);
					toogleLoader(false);
				}
			},
			function(err) {
				//TODO make error preview
				console.error(err);
				isLoading = false;
				count--;
				if (!count) {
					showListofPlugins(true);
					toogleLoader(false);
				}
			}
		);
	}
	Ps = new PerfectScrollbar('#' + "div_main", {});
};

function showListofPlugins(bAll) {
	elements.divMain.innerHTML = "";
	counter = 0;
	if (bAll) {
		for (const guid in allPlugins) {
			createPluginDiv(guid);	
		}
	} else {
		installedPlugins.forEach(function(el) {
			createPluginDiv(el.guid);
		});
	}

}

function createPluginDiv(guid) {
	// TODO добавить надпись что плагинов установленных нет
	// this function creates div (preview) for plugins
	// TODO может сделать динамическое количество элементов в одной строке
	if (counter <= 0 || counter >= 4) {
		row = document.createElement('div');
		row.className = "div_row"
		document.getElementById('div_main').append(row);
		counter = 1;
	}

	let div = document.createElement('div');
	div.id = guid;
	div.setAttribute('data-guid', guid);
	div.className = 'div_item';
	let installed = installedPlugins.find(function(el) {
		return (el.guid == guid);
	});
	
	let bHasUpdate = false;
	if (isDesctop && installed) {
		const installedV = (installed.obj.version ? installed.obj.version.split('.').join('') : 1);
		const lastV = (allPlugins[guid].config.version ? allPlugins[guid].config.version.split('.').join('') : installedV);
		if (lastV > installedV)
			bHasUpdate = true;
	}

	let imageUrl = allPlugins[guid].imageUrl;
	let variations = allPlugins[guid].config.variations[0];
	// TODO решить вопрос со scale, чтобы выбирать нужную иконку
	if (variations.icons2) {
		//
		let icon = variations.icons2[0];
		for (let i = 0; i < variations.icons2.length; i++) {
			if (theme.includes(variations.icons2[i].style)) {
				icon = variations.icons2[i];
				break;
			}
		}
		imageUrl += icon['200%'].normal;
	} else if (!variations.isSystem && imageUrl != '') {
		// TODO наверно надо переделать во всех плагинах, где это ещё осталось
		imageUrl += variations.icons[0];
	} else {
		imageUrl = "./resources/img/defaults/light/icon@2x.png"
	}
	// TODO подумать от куда брать цвет на фон под картинку (может в config добавить)
	let name = (bTranslate && allPlugins[guid].config.nameLocale) ? allPlugins[guid].config.nameLocale[shortLang] : allPlugins[guid].config.name;
	let description = (bTranslate && variations.descriptionLocale) ? variations.descriptionLocale[shortLang] : variations.description;
	let template = '<div class="div_image" onclick="onClickItem(event.target)">' +
						// временно поставил такие размеры картинки (чтобы выглядело симминтрично пока)
						'<img style="width:56px;" src="' + imageUrl + '">' +
					'</div>' +
					'<div class="div_description">'+
						'<span class="span_name">' + name + '</span>' +
						'<span class="span_description">' + description + '</span>' +
					'</div>' +
					'<div class="div_footer">' +
						(bHasUpdate
							? '<span class="span_update">' + translate["Update"] + '</span>'
							: ''
						)+''+
						(installed
							? (installed.canRemoved ? '<button class="btn-text-default btn_install" onclick="onClickRemove(event.target)">' + translate["Remove"] + '</button>' : '<div style="height:20px"></div>')
							: '<button class="btn-text-default btn_install" onclick="onClickInstall(event.target)">'  + translate["Install"] + '</button>'
						)
						+
					'</div>';
	div.innerHTML = template;
	row.append(div);
	counter++;
	Ps.update();
};

function onClickInstall(target) {
	toogleLoader(true, "Installation");
	let guid = target.parentNode.parentNode.getAttribute('data-guid');
	let message = {
		type : 'install',
		url : allPlugins[guid].configUrl.replace('raw.githubusercontent', 'github').replace('master', 'blob/master'),
		guid : guid
	};
	sendMessage(message);
};

function onClickUpdate(target) {
	toogleLoader(true, "Updating");
	let guid = target.parentElement.parentElement.parentElement.getAttribute('data-guid');
	let message = {
		type : 'update',
		url : allPlugins[guid].configUrl.replace('raw.githubusercontent', 'github').replace('master', 'blob/master'),
		guid : guid
	};
	sendMessage(message);
};

function onClickRemove(target) {
	toogleLoader(true, "Removal");
	let guid = target.parentNode.parentNode.getAttribute('data-guid');
	let message = {
		type : 'remove',
		guid : guid
	};
	sendMessage(message);
};

function onClickItem(target) {
	// There we will make preview for selected plugin
	// TODO продумать где брать offered by и где брать текс для этого блока (может из конфига) (так же переводы для него надо добавить)
	let offered = " Ascensio System SIA";
	let description = "Correct French grammar and typography. The plugin uses Grammalecte, an open-source grammar and typographic corrector dedicated to the French language.Correct French grammar and typography."

	elements.divSelected.classList.remove('hidden');
	elements.divSelectedMain.classList.remove('hidden');
	elements.arrow.classList.remove('hidden');
	let guid = target.parentNode.getAttribute('data-guid');
	elements.divBody.classList.add('hidden');
	let divPreview = document.createElement('div');
	divPreview.id = 'div_preview';
	divPreview.className = 'div_preview noselect';

	let installed = installedPlugins.find(function(el) {
		return (el.guid == guid);
	});

	let bHasUpdate = false;
	if (isDesctop && installed) {
		let installedV = installed.obj.version.split('.').join('');
		let lastV = allPlugins[guid].config.version.split('.').join('');
		if (lastV > installedV)
			bHasUpdate = true;
	}
	let confUrl = allPlugins[guid].configUrl.replace('raw.githubusercontent', 'github');
	let pluginUrl = (allPlugins[guid].configUrl.includes('sdkjs-plugins') ? confUrl.replace('master', 'tree/master').replace('config.json', '') : confUrl.replace('master/config.json', ''));
	// TODO проблема с тем, что в некоторых иконках плагинов есть отступ сверху, а в некоторых его нет (исходя их этого нужен разный отступ у span справа, чтобы верхние края совпадали)
	elements.divSelected.setAttribute('data-guid', guid);
	elements.imgIcon.setAttribute('src', target.children[0].src);
	elements.spanName.innerHTML = target.nextSibling.children[0].innerText;
	elements.spanOffered.innerHTML = offered;
	elements.spanSelectedDescr.innerHTML = description;
	elements.linkPlugin.setAttribute('href', pluginUrl);

	if (bHasUpdate) {
		elements.btnUpdate.classList.remove('hidden');
	} else {
		elements.btnUpdate.classList.add('hidden');
	}

	if (installed) {
		if (installed.canRemoved) {
			elements.btnRemove.classList.remove('hidden');
		} else {
			elements.btnRemove.classList.add('hidden');
		}
		elements.btnInstall.classList.add('hidden');
	} else {
		elements.btnRemove.classList.add('hidden');
		elements.btnInstall.classList.remove('hidden');
	}

	if (allPlugins[guid].config.variations[0].isVisual) {
		elements.imgScreenshot.setAttribute('src', './resources/img/screenshotes/' + guid + '.png');
		elements.imgScreenshot.classList.remove('hidden');
	} else {
		elements.imgScreenshot.classList.add('hidden');
	}

	setDivHeight();
};

function onSelectPreview(target, isOverview) {
	// change mode of preview
	if ( !target.classList.contains('span_selected') ) {
		$(".span_selected").removeClass("span_selected");
		target.classList.add("span_selected");

		if (isOverview) {
			document.getElementById('div_selected_info').classList.add('hidden');
			document.getElementById('div_selected_preview').classList.remove('hidden');
			setDivHeight();
		} else {
			document.getElementById('div_selected_preview').classList.add('hidden');
			document.getElementById('div_selected_info').classList.remove('hidden');

		}
	}
};

function setDivHeight() {
	// set height for div with image in preview mode
	if (Ps) Ps.update();
	// console.log(Math.round(window.devicePixelRatio * 100));
	let div = document.getElementById("div_selected_image");
	if (div) {
		let height = div.parentNode.clientHeight - div.previousElementSibling.clientHeight - 20 + "px";
		div.style.height = height;
		div.style.maxHeight = height;
	}
};

window.onresize = function() {
	setDivHeight();
	// TODO change icons for plugins preview for new scale
};

function getTranslation() {
	if (shortLang != "en") {
		makeRequest('./translations/langs.json').then(
			function(response) {
				let arr = JSON.parse(response);
				let fullName, shortName;
				for (let i = 0; i < arr.length; i++) {
					let file = arr[i];
					if (file == lang) {
						fullName = file;
						break;
					} else if (file.split('-')[0] == shortLang) {
						shortName = file;
					}
				}
				if (fullName || shortName) {
					bTranslate = true;
					makeRequest('./translations/' + (fullName || shortName) + '.json').then(
						function(res) {
							translate = JSON.parse(res);
							onTranslate();
						},
						function(err) {
							console.error(err);
							showMarketplace();
						}
					);
				} else {
					showMarketplace();
				}	
			},
			function(err) {
				console.error(err);
				showMarketplace();
			}
		);
	}
};

function onTranslate() {
	elements.linkNewPlugin.innerHTML = translate["Submit your own plugin"];
	elements.btnMyPlugins.innerHTML = translate["My plugins"];
	elements.btnMarketplace.innerHTML = translate["Marketplace"];
	elements.btnInstall.innerHTML = translate['Install'];
	elements.btnRemove.innerHTML = translate["Remove"];
	elements.btnUpdate.innerHTML = translate["Update"];
	document.getElementById('lbl_header').innerHTML = translate['Manage plugins'];
	document.getElementById('span_offered_caption').innerHTML = translate['Offered by'] + ': ';
	document.getElementById('span_overview').innerHTML = translate['Overview'];
	document.getElementById('span_info').innerHTML = translate['Info & Support'];
	document.getElementById('span_lern').innerHTML = translate['Learn how to use'] + ' ';
	document.getElementById('span_lern_plugin').innerHTML = translate['the plugin in'] + ' ';
	document.getElementById('span_contribute').innerHTML = translate['Contribute'] + ' ';
	document.getElementById('span_contribute_end').innerHTML = translate['to the plugin developmen or report an issue on'] + ' ';
	document.getElementById('span_help').innerHTML = translate['Get help'] + ' ';
	document.getElementById('span_help_end').innerHTML = translate['with the plugin functionality on our forum.'];
	document.getElementById('span_create').innerHTML = translate['Create a new plugin using'] + ' ';
	showMarketplace();
};

function showMarketplace() {
	elements.divBody.classList.remove('hidden');
	// убираем пока шапку, так как в плагине есть своя
	// elements.divHeader.classList.remove('hidden');
};