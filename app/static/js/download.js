var versionRegex = (
    /^b(\d{1,8})(?:(?!dev|tourney|test|peppy|arcade|ubertest\b)\w+\b)?(?:\.(\d{1,2}|))?(dev|tourney|test|peppy|arcade|cuttingedge|beta|ubertest)?$/
);

function downloadWineskinPackage(type) {
    var url = `https://cdn.lekuru.xyz/public/osx/osx-${type}.base.zip`;
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'blob';
    xhr.send();
    return new Promise(function (resolve, reject) {
        xhr.onload = function () {
            if (xhr.status == 200) {
                resolve(onPackageLoaded(xhr));
            } else {
                reject(new Error(xhr.statusText));
            }
        };
    });
}

function downloadGamePackage(client) {
    var url = `https://cdn.lekuru.xyz/clients/${client}.zip`;
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'blob';
    xhr.send();
    return new Promise(function (resolve, reject) {
        xhr.onload = function () {
            if (xhr.status == 200) {
                resolve(onPackageLoaded(xhr));
            } else {
                reject(new Error(xhr.statusText));
            }
        };
    });
}

async function mergePackages(osx, game, filename) {
    var osxFiles = osx.files;
    var gameFiles = game.files;
    var zip = new JSZip();
    Object.keys(osxFiles).forEach(function (file) {
        if (file.startsWith('osu!.app/')) {
            zip.file(file, osxFiles[file].async('blob'));
        }
    });
    Object.keys(gameFiles).forEach(function (file) {
        zip.file(`osu!.app/Contents/Resources/drive_c/osu!/${file}`, gameFiles[file].async('blob'));
    });
    var content = await zip.generateAsync({
        type: 'blob',
        platform: 'UNIX'
    });
    saveBlob(content, filename);
}

function saveBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function onPackageLoaded(xhr) {
    var responseBlob = xhr.response;
    return JSZip.loadAsync(responseBlob, {
        platform: 'UNIX'
    });
}

function getPackageType(client) {
    var match = versionRegex.exec(client);
    if (!match) return 'fallback';

    var build = parseInt(match[1]);
    if (build <= 20160403) return 'fallback';
    else return 'latest';
}

async function downloadOsxPackage(client) {
    type = getPackageType(client);

    Promise.all([downloadWineskinPackage(type), downloadGamePackage(client)])
        .then(function (packages) {
            mergePackages(packages[0], packages[1], `osx-${type}-${client}.zip`);
        })
        .catch(function (error) {
            console.error('Error downloading packages:', error);
        });
}

function displayCategory(category) {
    document.querySelectorAll(".client-container").forEach(function(client) {
        wasEnabled = client.style.display == 'block';

        if (wasEnabled)
        {
            client.style.display = 'none';
            return;
        }

        if (client.id == category)
        {
            client.style.display = 'block';
        }
        else
        { 
            client.style.display = 'none';
        }
    });

    document.querySelectorAll(".category").forEach(function(categoryLink) {
        if (categoryLink.textContent == category)
        {
            categoryLink.classList.add('selected');
        }
        else
        {
            categoryLink.classList.remove('selected');

        }
    });
}
