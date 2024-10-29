function final_trajectory = znorm_trajectory(data)
%     temp = reshape(data,1000,[]);
%     temp = normalize(temp,1,'range');
%     final_trajectory = reshape(temp, numel(temp), []);
%     final_trajectory = data;
      final_trajectory = normalize(data);
end
