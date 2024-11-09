import 'shpjs';
const fs = require('fs');

// Чтение SHP файла
function readFile(shpFilePath) {
    shpjs(shpFilePath).then(function(data) {
        console.log('Количество объектов:', data.length);
    
        // Перебор объектов
        data.forEach(function(feature, index) {
            console.log('Объект', index + 1, ':');
            console.log('Геометрия:', feature.geometry);
            console.log('Свойства:', feature.properties);
        });
    }).catch(function(error) {
        console.error('Ошибка при чтении SHP файла:', error);
    });    
}

const shpFilePath = 'data/House_1очередь_ЖК.shp';    
readFile(shpFilePath)

var map;

DG.then(function () {
    map = DG.map('map', {
        center: [55.565029, 37.452288],
        zoom: 13
    });

    DG.marker([55.563984, 37.407784]).addTo(map).bindPopup('Вы кликнули по мне!');
    // создает ломаную красного цвета из массива точек LatLng
    var latlngs = [
        [55.565657, 37.408957],
        [55.565885, 37.409588]
    ];
    var polyline = DG.polyline(latlngs, {color: 'red'}).addTo(map);

    // создает красный многоугольник из массива точек LatLng
    var latlngs = [[55.566431, 37.410476],[55.566558, 37.410292],
                    [55.566650, 37.410490],[55.566524, 37.410674]];
    var polygon = DG.polygon(latlngs, {color: 'red'}).addTo(map);
    // увеличиваем масштаб так, чтобы было видно всю ломаную
    // map.fitBounds(polyline.getBounds());
});

// Функция для чтения SHP файла
// function readFile(url) {
//     fetch(url)
//         .then(response => response.arrayBuffer())
//         .then(buffer => {
//             shp(buffer).then(function(data) {
//                 console.log('Количество объектов:', data.length);

//                 // Перебор объектов
//                 data.forEach(function(feature, index) {
//                     console.log('Объект', index + 1, ':');
//                     console.log('Геометрия:', feature.geometry);
//                     console.log('Свойства:', feature.properties);
//                 });
//             }).catch(function(error) {
//                 console.error('Ошибка при чтении SHP файла:', error);
//             });
//         })
//         .catch(function(error) {
//             console.error('Ошибка при загрузке SHP файла:', error);
//         });
// }
