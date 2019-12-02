<template>
  <div>
    <div class="init">
      <p class="title">Initialize the storage</p>
      <button v-on:click="openInitConfirmation()">initialize</button>
    </div>
    <div class="card-container">
      <div class="card card-file">
        <div class="file-commands">
          <div>
            <div>
              <p class="title">Create an empty file</p>
              <input type="text" v-model="createFileName" placeholder="absolute name">
              <p>
                <button v-on:click="createFile()">create file</button>
              </p>
              <p style="color:#ff3a50;">{{createError}}</p>
            </div>
            <div>
              <p class="title">Download a file</p>
              <input type="text" v-model="downloadfileName" placeholder="absolute name">
              <p>
                <button v-on:click="downloadFile()">download file</button>
              </p>
              <p style="color:#ff3a50;">{{downloadError}}</p>
            </div>
            <div>
              <p class="title">Upload a file</p>
              <p>
                <input type="file" ref="file" placeholder="upload a file" style="border: none;">
              </p>
              <p>
                save to:
                <input type="text" v-model="directory" placeholder="/directory1/directory2">
              </p>
              <p>
                save as:
                <input type="text" v-model="name" placeholder="file name">
              </p>
              <p>
                <button v-on:click="uploadFile()">upload file</button>
              </p>
              <p style="color:#ff3a50;">{{uploadError}}</p>
            </div>
          </div>
          <div>
            <div>
              <p class="title">Delete a file</p>
              <input type="text" v-model="deleteFileName" placeholder="absolute name">
              <p>
                <button v-on:click="deleteFile()">delete file</button>
              </p>
              <p style="color:#ff3a50;">{{deleteError}}</p>
            </div>
            <div>
              <p class="title">Get information about a file</p>
              <input type="text" v-model="getInfoFileName" placeholder="absolute name">
              <p>
                <button v-on:click="getFileInfo()">file info</button>
              </p>
              <p style="color:#ff3a50;">{{infoError}}</p>
              <div v-if="fileInfo !== undefined && fileInfo.size !== undefined">
                <p>size of the file: <a style="color: #ff3a50;">{{fileInfo.size}}</a></p>
                <p>time of last access: <a style="color: #ff3a50;">{{printDate(fileInfo.last_accessed)}}</a></p>
                <p>time of last modification: <a style="color: #ff3a50;">{{printDate(fileInfo.last_modified)}}</a></p>
              </div>
            </div>
            <div>
              <p class="title">Copy a file</p>
              <p>file: <input type="text" v-model="copyFromFileName" placeholder="absolute name"></p>
              <p>as:
                <input type="text" v-model="copyToFileName" placeholder="absolute name">
              </p>
              <p>
                <button v-on:click="copyFile()">copy file</button>
              </p>
              <p style="color:#ff3a50;">{{copyError}}</p>
            </div>
            <div>
              <p class="title">Move a file</p>
              <p>from:
                <input type="text" v-model="moveFromFileName" placeholder="absolute name">
              </p>
              <p>to:
                <input type="text" v-model="moveToFileName" placeholder="absolute name">
              </p>
              <p>
                <button v-on:click="moveFile()">move file</button>
              </p>
              <p style="color:#ff3a50;">{{moveError}}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="card card-dir">
        <div class="file-commands">
          <div>
            <p class="title">Current directory: <a style="color: #ff3a50;">{{currentPath}}</a></p>
            <div>
              <p class="title">Move to another directory ('cd' command)</p>
              <p><input type="text" :placeholder="currentPath" v-model="cdDirectory"></p>
              <p>
                <button v-on:click="cdRequest()">move to directory</button>
              </p>
              <p style="color:#ff3a50;">{{cdError}}</p>
            </div>
            <div>
              <p class="title">List all files and directories ('ls' command)</p>
              <p>directory (optional):
                <input type="text" v-model="lsDirectory"></p>
              <p>
                <button v-on:click="getLs()">list</button>
              </p>
              <a v-for="(entity, i) in lsList" :key="i"
                 :style="(entity.color === 'true' ? 'color: #ff3a50;' : 'color: #0864b0;') + 'font-weight:bolder; font-size:18px;'">
                {{ entity.name }}
              </a>
            </div>
          </div>
          <div>
            <div>
              <p class="title">Make a directory</p>
              <input type="text" placeholder="absolute name" v-model="mkDirectory">
              <p>
                <button v-on:click="mkdirRequest()">make directory</button>
              </p>
              <p style="color:#ff3a50;">{{mkError}}</p>
            </div>
            <div>
              <p class="title">Delete a directory</p>
              <input type="text" placeholder="absolute name" v-model="delDirectory">
              <p>
                <button v-on:click="openDeleteConfirmation()">delete directory</button>
              </p>
              <p style="color:#ff3a50;">{{delError}}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

        <div id="initModal" class="modal" :style="isInitOpen ? 'display: block;' : 'display: none;'">
          <div class="modal-content">
            <p>Please enter the namenode IP</p>
            <input type="text" v-model="namenodeIP">
            <button v-on:click="saveIP()">save</button>
          </div>
        </div>

    <div id="initConfirmation" class="modal" v-if="initConfirmationOpen">
      <div class="modal-content">
        <p>The root directory contains:</p>
        <a v-for="(entity, i) in initConfirmList" :key="i"
           :style="(entity.color === 'true' ? 'color: #ff3a50;' : 'color: #0864b0;') + 'font-weight:bolder; font-size:18px;'">
          {{ entity.name }}
        </a>
        <p>Are you sure you want to clean the storage?</p>
        <button v-on:click="closeInitConfirmation()">back</button>
        <button v-on:click="init()">ok</button>
      </div>
    </div>

    <div id="availableAmount" class="modal" v-if="availableShow">
      <div class="modal-content">
        <p>Available storage capacity:</p>
        <p style="color: #ff3a50;">{{availableAmount}} bytes</p>
        <button v-on:click="closeAvailable()">ok</button>
      </div>
    </div>

    <div id="deleteConfirmation" class="modal" v-if="deleteConfirmationOpen">
      <div class="modal-content">
        <p>The directory <a style="color: #ff3a50;">{{delDirectory}}</a> contains:</p>
        <a v-for="(entity, i) in deleteConfirmList" :key="i"
           :style="(entity.color === 'true' ? 'color: #ff3a50;' : 'color: #0864b0;') + 'font-weight:bolder; font-size:18px;'">
          {{ entity.name }}
        </a>
        <p>Are you sure you want to delete the directory?</p>
        <button v-on:click="closeDeleteConfirmation()">back</button>
        <button v-on:click="deleteDirectory()">ok</button>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "MainPage",
    data() {
      return {
        isInitOpen: true,
        namenodeIP: "",
        chunkSize: 1 * 1024 * 1024,
        currentPath: "/",
        directory: "",
        name: "",
        datanodeIP: "",
        fileStorage: {},
        downloadfileName: "",
        deleteFileName: "",
        getInfoFileName: "",
        copyFromFileName: "",
        copyToFileName: "",
        moveFromFileName: "",
        moveToFileName: "",
        createFileName: "",
        createError:"",
        datanodeIPsList: {},
        lsDirectory: "",
        cdDirectory: "",
        mkDirectory: "",
        fileInfo: {},
        cdError: "",
        lsError: "",
        downloadError: "",
        downloadSuccess: "",
        lsList: [],
        delDirectory: "",
        initConfirmList: [],
        initConfirmationOpen: false,
        availableAmount: "",
        availableShow: false,
        deleteConfirmationOpen: false,
        deleteConfirmList: [],
        delError: "",
        moveError: "",
        copyError: "",
        infoError: "",
        deleteError: "",
        mkError: "",
        uploadError: "",
        datanodeAnswered: false,
      }
    },
    created: {},
    methods: {
      closeDeleteConfirmation() {
        this.deleteConfirmationOpen = false;
      },
      async openDeleteConfirmation() {
        this.deleteConfirmList = [];
        await this.lsRequest(this.delDirectory);
        this.deleteConfirmList = this.lsResponse;
        console.log(this.deleteConfirmList);
        if (this.deleteConfirmList.length === 0) this.deleteDirectory();
        else if ((this.deleteConfirmList.length === 1) && (this.deleteConfirmList[0].name === 'no such directory')) {
          this.delError = 'no such directory';
        } else this.deleteConfirmationOpen = true;
      },
      closeAvailable() {
        this.availableShow = false;
      },
      async openInitConfirmation() {
        this.initConfirmList = [];
        await this.lsRequest("/");
        this.initConfirmList = this.lsResponse;
        console.log(this.initConfirmList);
        if (this.initConfirmList.length === 0) this.init();
        else this.initConfirmationOpen = true;
        console.log(this.initConfirmationOpen)
      },
      closeInitConfirmation() {
        this.initConfirmationOpen = false;
      },
      saveIP() {
        if (this.namenodeIP !== "") this.isInitOpen = false;
      },
      printDate(dateString) {
        dateString = dateString.toString() * 1000;
        const date = new Date(dateString);
        let options = {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
          second: 'numeric'
        };
        return date.toLocaleDateString("en-US", options);
      },
      async uploadFile() {
        const file = this.$refs.file.files[0];
        let fileName = this.directory + "/" + this.name + "." + file.name.split('.').pop();
        if (fileName[0] !== "/") fileName = "/" + fileName;
        // this.datanodeIP = "10.91.91.190:5000";

        await this.getDatanodeToUpload(fileName);

        const chunksNumber = Math.ceil(file.size / this.chunkSize);
        const chunksQueue = new Array(chunksNumber).fill().map((_, index) => index).reverse();
        while (!!chunksQueue.length && chunksQueue.length > 0) {
          let chunkId = chunksQueue.pop();
          console.log("Uploading chunk #" + chunkId + "...");
          let begin = chunkId * this.chunkSize;
          let currentChunk = file.slice(begin, begin + this.chunkSize);
          this.uploadChunk(
            this.datanodeIP,
            chunkId.toString(),
            currentChunk,
            chunksNumber,
            fileName,
            "1",
            file.size.toString()
          )
            .then(() => {
              this.uploadError = "";
              console.log("chunk #" + chunkId + " uploaded successfully");
            })
            .catch(() => {
              console.log("chunk #" + chunkId + " uploading failed");
              this.uploadError = "Connection error. Please, try again."
              chunksQueue.push(chunkId);
            });
        }
        console.log("The file uploaded");
      },
      async downloadFile() {
        let fileName = this.downloadfileName;
        if (fileName[0] !== "/") fileName = "/" + fileName;
        await this.getDatanodeToDownload(fileName);
        this.datanodeAnswered = false;
        let i = 0;

        while ((!this.datanodeAnswered) && (i < this.datanodeIPsList.length)) {
          let reqUrl = "http://" + this.datanodeIPsList[i] + "/download";
          await this.downloadRequest(fileName, reqUrl);
          i++;
        }

        if (!this.datanodeAnswered) {
          this.downloadError = "sorry, no such file was found";
        } else {
          this.downloadError = "";
        }
      },
      deleteFile() {
        let fileName = this.deleteFileName;
        if (fileName[0] !== "/") fileName = "/" + fileName;
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/delete_file";
          xhr.open("GET", url);
          xhr.setRequestHeader("File-Name", fileName);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.deleteError = "";
              resolve();
            } else {
              this.deleteError = "sorry, no such file was found"
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      getFileInfo() {
        let fileName = this.getInfoFileName;
        if (fileName[0] !== "/") fileName = "/" + fileName;
        this.fileInfo = {};
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/info";
          xhr.open("GET", url);
          xhr.setRequestHeader("File-Name", fileName);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.fileInfo = JSON.parse(xhr.response);
              this.infoError = "";
              resolve();
            } else {
              this.infoError = "sorry, no such file was found"
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      copyFile() {
        let fileName1 = this.copyFromFileName;
        let fileName2 = this.copyToFileName;
        if (fileName1[0] !== "/") fileName1 = "/" + fileName1;
        if (fileName2[0] !== "/") fileName2 = "/" + fileName2;

        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/copy";
          xhr.open("GET", url);
          xhr.setRequestHeader("File-Name-Old", fileName1);
          xhr.setRequestHeader("File-Name-New", fileName2);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.copyError = "";
              resolve();
            } else {
              this.copyError = "incorrect request"
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      moveFile() {
        let fileName1 = this.moveFromFileName;
        let fileName2 = this.moveToFileName;
        if (fileName1[0] !== "/") fileName1 = "/" + fileName1;
        if (fileName2[0] !== "/") fileName2 = "/" + fileName2;

        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/move";
          xhr.open("GET", url);
          xhr.setRequestHeader("File-Name-Old", fileName1);
          xhr.setRequestHeader("File-Name-New", fileName2);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.moveError = "";
              resolve();
            } else {
              this.moveError = "incorrect request"
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      init() {
        this.initConfirmationOpen = false;
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/init";
          xhr.open("GET", url);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.availableAmount = xhr.response;
              this.availableShow = true;
              resolve();
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      uploadChunk(
        datanodeIP,
        chunkId,
        chunk,
        chunkNumber,
        fileName,
        fileId,
        fileSize) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + datanodeIP + "/upload";
          xhr.open("POST", url);
          xhr.setRequestHeader("Content-Type", "application/octet-stream");
          xhr.setRequestHeader("Chunk-Id", chunkId);
          xhr.setRequestHeader("Chunk-Number", chunkNumber);
          xhr.setRequestHeader("File-Name", fileName);
          xhr.setRequestHeader("File-Id", fileId);
          xhr.setRequestHeader("File-Length", fileSize);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              resolve();
            }
          };
          xhr.onerror = reject;
          xhr.send(chunk);
        });
      },
      getDatanodeToUpload(fileName) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/write";
          xhr.open("GET", url);
          xhr.setRequestHeader("File-Name", fileName);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.datanodeIP = xhr.response;
              this.uploadError = "";
              resolve();
            } else {
              this.uploadError = "incorrect request"
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      createFile() {
        let fileName = this.createFileName;
        if (fileName[0] !== "/") fileName = "/" + fileName;
        if (fileName.length !== 1) {
          return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const url = "http://" + this.namenodeIP + "/create";
            xhr.open("GET", url);
            xhr.setRequestHeader("File-Name", fileName);
            xhr.onreadystatechange = () => {
              if (xhr.readyState === 4 && xhr.status === 200) {
                this.createError = "";
                resolve();
              } else {
                this.createError = "incorrect request";
              }
            };
            xhr.onerror = reject;
            xhr.send(null);
          });
        }
      },
      getDatanodeToDownload(fileName) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/read";
          xhr.open("GET", url);
          xhr.setRequestHeader("File-Name", fileName);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.downloadError = "";
              this.datanodeIPsList = JSON.parse(xhr.response);
              console.log(this.datanodeIPsList);
              resolve();
            } else {
              this.downloadError = "sorry, no such file was found";
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      cdRequest() {
        let directory = this.cdDirectory;
        if (directory[0] !== '/') directory = "/" + directory;
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/cd";
          xhr.open("GET", url);
          xhr.setRequestHeader("Directory", directory);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.cdError = "";
              this.currentPath = directory;
              console.log("moved");
              resolve();
            } else if (xhr.readyState === 4 && xhr.status === 400) {
              this.cdError = "no such directory";
              resolve();
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      async getLs() {
        let directory;
        if (this.lsDirectory === "") directory = this.currentPath;
        else directory = this.lsDirectory;
        if (directory[0] !== "/") directory = "/" + directory;
        this.lsList = [];
        await this.lsRequest(directory);
        this.lsList = this.lsResponse;
      },
      lsRequest(directory) {
        if (directory[0] !== '/') directory = "/" + directory;
        this.lsResponse = [];
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/ls";
          xhr.open("GET", url);
          xhr.setRequestHeader("Directory", directory);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.lsError = "";
              let lsResponse = xhr.response;
              console.log(lsResponse);
              if (lsResponse === "{}") resolve();
              else {
                let list = lsResponse.toString().replace("{", "").replace("}", "").split(",");
                for (let value of list) {
                  let tuple = value.replace(" ", "").replace("\"", "").replace("\'", "").split(":");
                  let name = tuple[0].replace(" ", "").replace("\"", "").replace("\'", "");
                  let color = tuple[1].replace(" ", "").replace("\"", "").replace("\'", "");
                  tuple = {};
                  tuple.name = name;
                  tuple.color = color;
                  this.lsResponse.push(tuple)
                }
                this.lsResponse.sort(function (a, b) {
                  let nameA = a.name.toLowerCase(), nameB = b.name.toLowerCase();
                  if (nameA < nameB)
                    return -1;
                  if (nameA > nameB)
                    return 1;
                  return 0
                });
                resolve();
              }
            } else if (xhr.readyState === 4) {
              let tuple = {};
              tuple.name = "no such directory";
              tuple.color = "true";
              this.lsResponse.push(tuple);
              resolve();
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      mkdirRequest() {
        let directory = this.mkDirectory;
        if (directory[0] !== '/') directory = "/" + directory;
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/mkdir";
          xhr.open("GET", url);
          xhr.setRequestHeader("Directory", directory);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.mkError = "";
              resolve();
            } else {
              this.mkError = "incorrect request";
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      deleteDirectory() {
        let directory = this.delDirectory;
        if (directory[0] !== '/') directory = "/" + directory;
        this.deleteConfirmationOpen = false;
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          const url = "http://" + this.namenodeIP + "/delete_dir";
          xhr.open("GET", url);
          xhr.setRequestHeader("Directory", directory);
          xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.delError = "";
              resolve();
            } else {
              this.delError = "no such directory";
            }
          };
          xhr.onerror = reject;
          xhr.send(null);
        });
      },
      downloadRequest(fileName, reqUrl) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open("GET", reqUrl);
          xhr.setRequestHeader("File-Name", fileName);
          xhr.responseType = 'blob';
          xhr.onreadystatechange = () => {
            let a;
            if (xhr.readyState === 4 && xhr.status === 200) {
              this.datanodeAnswered = true;
              a = document.createElement('a');
              let url = window.URL.createObjectURL(xhr.response);
              a.href = url;
              a.download = fileName.split('/').pop();
              a.style.display = 'none';
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
              resolve();
            } else {
              this.datanodeAnswered = false;
            }
          };
          xhr.onerror = () => {
            this.datanodeAnswered = false;
            resolve();
          };
          xhr.send(null);
        });
      }
    }
  }
</script>

<style scoped>

  .init {
    display: flex;
    justify-content: center;
    flex-flow: column;
    align-items: center;
    margin-bottom: 30px;
  }

  .card-container {
    display: flex;
    justify-content: space-around;
  }

  .card {
    width: 45%;
    display: flex;
    flex-flow: column;
    align-items: baseline;

    background-color: aliceblue;
  }


  .file-commands {
    display: flex;
    flex-flow: initial;
    justify-content: space-between;
    width: 90%;
    margin: 30px;
  }

  .file-commands > div > div, .card-dir > div {
    margin-bottom: 40px;
  }

  p {
    text-align: left;
    margin: 7px 0 7px;
    font-size: 18px;
  }

  p.title {
    font-weight: bolder;
  }

  button {
    background-color: white;
    color: black;
    border: 2px solid #089edd;
    padding: 6px 15px;
    font-size: 16px;
    -webkit-transition-duration: 0.4s; /* Safari */
    transition-duration: 0.4s;
    background-color: aliceblue;
  }

  button:hover {
    background-color: #089edd; /* Green */
    color: white;
  }

  input {
    border: none;
    border-bottom: 2px solid #089edd;
    padding: 4px;
    font-size: 16px;
    background-color: aliceblue;
  }

  input[type=text]:focus {
    outline: none !important;
  }

  .modal {
    position: fixed; /* Stay in place */
    z-index: 1; /* Sit on top */
    padding-top: 100px; /* Location of the box */
    left: 0;
    top: 0;
    width: 100%; /* Full width */
    height: 100%; /* Full height */
    overflow: auto; /* Enable scroll if needed */
    background-color: rgb(0, 0, 0); /* Fallback color */
    background-color: rgba(0, 0, 0, 0.4); /* Black w/ opacity */
  }

  /* Modal Content */
  .modal-content {
    background-color: #fefefe;
    margin: auto;
    padding: 20px;
    border: 1px solid #888;
    width: 30%;
    text-align: center;
  }

  .modal-content p {
    text-align: center;
  }

  /* The Close Button */
  .close {
    color: #aaaaaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
  }

  .close:hover,
  .close:focus {
    color: #000;
    text-decoration: none;
    cursor: pointer;
  }
</style>
