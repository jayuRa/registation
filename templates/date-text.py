#   $(document).ready(function(){
#     var countryid=$('#country').val()
#     //alert(countryid)
#     getState(countryid)
#   });
#   $('#country').on('change', function () {
#           $('#state').empty()
#           $('#city').empty()
#            var countryid=$(this).val();
#            getState(countryid)
#         });

#   function getState(countryid){
#     $.ajax({
#             url:'/state',
#             method:'post',
#             dataType:'JSON',
#             data:{country_data:countryid},
#             success:function(state_result){
#                   var ele=$('[name="state_id"]').val();
#                   var element=parseInt(ele);
#                   let html_data='<option value="">Select State</option>'
#                   $.each(state_result,function(index,value){
#                    if (element==index){
#                    html_data +='<option value="'+index+'"selected>'+value+'</option>'
#                    } 
#                    else{ 
#                    html_data +='<option value="'+index+'">'+value+'</option>'
#                    }
#                   });
#                   $("#state").html(html_data);
#                 }
#             });
#   }
#   $(document).ready(function(){
#     var stateid= $('[name="state_id"]').val();
#     //alert(stateid)
#     getcity(stateid)
#   });
#   $('#state').on('change', function () {      
#            var stateid=$(this).val();
#            getcity(stateid)
#         });
#   function getcity(stateid){
#     $.ajax({
#             url:'/city',
#             method:'post',
#             dataType:'JSON',
#             data:{state_data:stateid},
#             success:function(city_result){
#                   var ele1=$('[name="city_id"]').val();
#                   var element1=parseInt(ele1);
#                   let html_data='<option value="">Select city</option>'
#                   $.each(city_result,function(id,value){
#                    if (element1==id){
#                    html_data +='<option value="'+id+'"selected>'+value+'</option>'
#                    } 
#                    else{ 
#                    html_data +='<option value="'+id+'">'+value+'</option>'
#                    }
#                   });
#                   $("#city").html(html_data);
#                 }
#             });
#   }        