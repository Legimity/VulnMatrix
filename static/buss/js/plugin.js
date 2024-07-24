$('.dropify').dropify({
  messages: {
    'default': 'Drag and drop a file here or click',
    'replace': 'Drag and drop or click to replace',
    'remove': 'Remove',
    'error': 'Ooops, something wrong appended.'
  },
  error: {
    'fileSize': 'The file size is too big (1M max).'
  }
});

$('#up-type').change(function () {
  if ($(this).val() == 'json') {
    $('.uploadjson').css('display', '');
    $('.uploadfile').css('display', 'none');
  } else if ($(this).val() == 'file') {
    $('.uploadjson').css('display', 'none');
    $('.uploadfile').css('display', '');
  } else if ($(this).val() == 'docker-compose') {
    $('.uploadjson').css('display', '');
    $('.uploadfile').css('display', 'none');
  } else {
    $('.uploadjson').css('display', 'none');
    $('.uploadfile').css('display', 'none');
  }
});



$('#add').click(function () {
  name = $('#env-name').val();
  info = $('#env-info').val();
  author = $('#env-author').val();
  risk = $('#env-risk').val();
  info = $('#env-info').val();
  tags = $('#env-tags').val();
  hub = $('#env-hub').val();
  type = $('#env-type').val();
  port = $('#env-port').val();
  flag = $('#env-flag').val();
  path = $('#env-fileupload').val();
  syspassjson = $('#env-syspass-json').val();
  syspassfile = $('#env-syspass-file').val();
  filename = path.substring(path.lastIndexOf('\\')).split('.')[0];
  isupload = $('#env-isupload').val();
  $.ajaxFileUpload({
    url: "/add_images",
    secureuri: false,
    type: "POST",
    data: {
      name: name,
      info: info,
      isupload: isupload,
      type: type,
      flag: flag,
      author: author,
      risk: risk,
      tags: tags,
      hub: hub,
      port: port,
      syspassjson: syspassjson,
      syspassfile: syspassfile
    },
    dataType: "json",
    fileElementId: "env-fileupload",
    success: function (e) {
    },
    error: function (e) {
      if (e.responseText == 'success') {
        swal("新增成功,正在后台进行下载！", '', "success");
        $('.confirm').click(function () {
          $('#close').click();
          location.reload();
        });

      } else {
        swal("新增失败", "请检查数据是否完整或是否存在特殊字符!", "error")
      }
    }
  });

});


$('#add_envs').click(function () {
  console.log('add_envs');
  name = $('#env-name').val();
  info = $('#env-info').val();
  // author = $('#env-author').val();
  // risk = $('#env-risk').val();
  tags = $('#env-tags').val();
  // hub = $('#env-hub').val();
  // type = $('#env-type').val();
  // port = $('#env-port').val();
  // flag = $('#env-flag').val();
  // path = $('#env-fileupload').val();
  // syspassjson = $('#env-syspass-json').val();
  syspassfile = $('#env-syspass-file').val();
  // filename = path.substring(path.lastIndexOf('\\')).split('.')[0];
  // isupload = $('#env-isupload').val();

  // var fileInput = $('#env-fileupload')[0].files[0]; // 获取文件输入
  console.log(name, info, tags);
  $.ajaxFileUpload({
    url: "/add_envs",
    secureuri: false,
    type: "POST",
    data: {
      name: name,
      info: info,
      // isupload: isupload,
      // type: type,
      // flag: flag,
      // author: author,
      // risk: risk,
      tags: tags,
      // hub: hub,
      // port: port,
      // syspassjson: syspassjson,
      syspassfile: syspassfile,

    },
    dataType: "json",
    fileElementId: "env-fileupload",
    success: function (e) {

    },
    error: function (e) {
      if (e.responseText == 'success') {
        swal("新增成功,正在后台进行下载！", '', "success");
        $('.confirm').click(function () {
          $('#close').click();
          location.reload();
        });

      } else {
        swal("新增失败", "请检查数据是否完整或是否存在特殊字符!", "error")
      }
    }
  });

});

// $(document).ready(function () {
//   $('#add_envs').click(function (e) {
//     e.preventDefault(); // 防止默认表单提交行为

//     var name = $('#env-name').val();
//     var info = $('#env-info').val();
//     var tags = $('#env-tags').val();
//     console.log(name, info, tags);
//     var fileInput = $('#env-fileupload')[0].files[0]; // 获取文件输入

//     // 创建FormData对象并附加表单数据和文件·
//     var formData = new FormData();
//     formData.append('name', name);
//     formData.append('info', info);
//     formData.append('tags', tags);
//     if (fileInput) {
//       formData.append('env-fileupload', fileInput);
//     }

//     // 发送Ajax请求
//     $.ajax({
//       url: '/add_envs', // 替换为你的实际后端URL
//       type: 'POST',
//       data: formData,
//       contentType: false, // 必须设置为false，告诉jQuery不要处理数据
//       processData: false, // 必须设置为false，告诉jQuery不要设置Content-Type
//       dataType: 'json', // 预期从服务器接收到JSON格式的响应
//       success: function (response) {
//         if (response.success) {
//           swal("新增成功,正在后台进行下载！", '', "success");
//           $('.confirm').click(function () {
//             $('#close').click();
//             location.reload();
//           });
//         } else {
//           swal("新增失败", "请检查数据是否完整或是否存在特殊字符!", "error");
//         }
//       },
//       error: function (error) {
//         swal("新增失败", "请检查数据是否完整或是否存在特殊字符!", "error");
//       }
//     });
//   });
// });
