function updatelist(folderlist, folders, clear = false) {
    if (clear)
        folderlist.innerHTML = "";
    folders.forEach(folder => {
        let prevContent = folderlist.innerHTML;
        let icon = "";
        if (folder["type"] == "folder") {
            icon = "<i class=\"fa-solid fa-folder\"></i>"
        }
        else {
            icon = "<i class=\"fa-solid fa-file\"></i>"
        }
        let newContent = "<div class=\"folder\">" + icon + "<p class=\"" + folder["type"] + "name\">" + folder["name"] + "</p></div>"
        folderlist.innerHTML = prevContent + newContent;
    });

    let htmlfolders = document.getElementsByClassName("folder");
    for (const hfolder of htmlfolders) {
        hfolder.addEventListener('click', function (event) {
            if (this) {
                let para = this.querySelector("p.foldername");
                if (para) {
                    let name = para.innerText;
                    let classname = para.className;
                    let childfolder = "";
                    folders.forEach((folder) => {
                        if (folder["name"] == name) {
                            childfolder = folder;
                        }
                    });
                    updatelist(folderlist, childfolder["content"], true);
                }
            }
        });
    }
}

let folderlist = document.querySelector("#folderlist");
let homebtn = document.querySelector(".home");
homebtn.addEventListener('click', function (event) {
    updatelist(folderlist, folders, true);
});
updatelist(folderlist, folders);