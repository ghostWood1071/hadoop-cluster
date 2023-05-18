var app = angular.module('video', []);

app.controller('video_query', ($scope, $http)=>{
    $scope.playState = 0;
    $scope.people = [{upper: null, lower: null}];
    $scope.objects = [{name: null, color:null}];
    $scope.colors = [];
    $scope.cams = [];

    $http({
        method: 'GET',
        url: '/cameras'
    }).then((res)=>{
        $scope.cams = res.data;
        $scope.cams.unshift(null);
    })

    $http({
        method: 'GET',
        url: '/object-names'
    }).then((res)=>{
        $scope.objectNames = res.data;
    });

    $http({
        method: 'GET',
        url: '/colors'
    }).then((res)=>{
        $scope.colors = res.data;
        $scope.colors.unshift(null);
        console.log(res);
    });

    $scope.haveObjectChange = ()=>{
        console.log($scope.haveObject); 
        if($scope.haveObject)
            $('.object').prop('disabled', true);
        else
            $('.object').prop('disabled', false);
    }

    $scope.haveHumanChange = ()=>{
        console.log($scope.haveHuman); 
        if($scope.haveHuman)
            $('.human').prop('disabled', true);
        else
            $('.human').prop('disabled', false);
    }

    $scope.justHumanChange = ()=>{
        console.log($scope.justHuman);
        if($scope.justHuman)
            $('.object-prop').css('display', 'none');
        else
            $('.object-prop').css('display', 'block');
    }

    $scope.justObjectChange = ()=>{
        console.log($scope.justObject);
        if($scope.justObject)
            $('.human-prop').css('display', 'none');
        else
            $('.human-prop').css('display', 'block');
    }

    $scope.addPerson = ()=>{
        $scope.people.push({upper: null, lower: null});
    }

    $scope.delPerson = (idx)=>{
        if($scope.people.length <=1)
            return;
        $scope.people.splice(idx, 1);
    }

    $scope.addObj = ()=>{
        $scope.objects.push({name: null, color: null});
    }

    $scope.delObj = (idx)=>{
        if($scope.objects.length<=1)
            return;
        $scope.objects.splice(idx, 1);
    }

    $scope.search = ()=>{
        $('.overlay').css('display', 'block')

        $scope.frames = []
        $scope.segments = []

        let from_time = 0;
        let to_time =0;
        if ($scope.from_time)
            from_time = $scope.from_time.getTime();
        if ($scope.to_time)
            to_time = $scope.to_time.getTime();
        
        $http({
            method: 'POST',
            url: '/segments',
            data: {
                just_human: $scope.justHuman,
                just_object: $scope.justObject,
                have_human: $scope.haveHuman,
                have_object: $scope.haveObject,
                camera: $scope.camera,
                people: $scope.people,
                objs: $scope.objects,
                time_ranges: [from_time, to_time]
            }
        }).then((res)=>{
            $scope.segments = res.data;
            console.log($scope.segments);
            $('.overlay').css('display', 'none');
        },(err)=>{
            console.log(err);
            $('.overlay').css('display', 'none');
        });
    }

    $scope.get_frames = (segment_id, video_id, url)=>{
        $('.overlay').css('display', 'block');
        console.log(segment_id)
        let from_time = 0;
        let to_time =0;
        if ($scope.from_time)
            from_time = $scope.from_time.getTime();
        if ($scope.to_time)
            to_time = $scope.to_time.getTime();
        // $scope.video_source = '/video?link='+url;

        // let player = document.getElementById('player');
        // while (player.childElementCount >0)
        //     player.removeChild()
        // let source = document.createElement('source');
        // source.setAttribute('src', $scope.video_source);
        // source.setAttribute('type', 'video/webm');
        // player.appendChild(source)

        $http({
            method: 'POST',
            url: `/frames?segment_id=${segment_id}&video_id=${video_id}`,
            data: {
                just_human: $scope.justHuman,
                just_object: $scope.justObject,
                have_human: $scope.haveHuman,
                have_object: $scope.haveObject,
                camera: $scope.camera,
                people: $scope.people,
                objs: $scope.objects,
                time_ranges: [from_time, to_time]
            }
        }).then((res)=>{
            $scope.frames = res.data;
            $('.overlay').css('display', 'none');
        }, (err)=>{
            console.log(err);
            $('.overlay').css('display', 'none');
        })
    }


    $scope.query = ()=>{
        console.log($scope.cols);
        console.log($scope.command);
        $http({
            method: 'GET',
            url: '/query?command='+$scope.command.trim()+"&cols="+$scope.cols.trim(),
            data: $scope.command
        }).then((res)=>{
            $scope.results = res.data;
            if($scope.results.length>0){
                $scope.src = 'data:image/jpeg;base64,'+$scope.results[0].frame;
                $scope.index = 0;
            }
        }, (err)=>{
            console.log(err);
        });
    }

    $scope.next = ()=>{
        $scope.index += 1;
        if($scope.index>=$scope.results.length)
            $scope.index = 0;
        $scope.src = 'data:image/jpeg;base64,'+$scope.results[$scope.index].frame;
     
    }

    $scope.prev = ()=>{
        $scope.index -= 1;
        if($scope.index < 0)
            $scope.index = $scope.results.length-1;
        $scope.src = 'data:image/jpeg;base64,'+$scope.results[$scope.index].frame;
    }

    $scope.play = ()=>{
        if($scope.playState == 0){
            setInterval(()=>{
                $scope.next();
                
            }, 300)
        }
    }
});