package com.wl.xc.modelfun.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.wl.xc.modelfun.entities.po.NerAutoLabelResultPO;

/**
 * @version 1.0
 * @date 2022/5/25 18:37
 */
public interface NerAutoLabelResultForBatchMapper extends BaseMapper<NerAutoLabelResultPO> {

  int insertSelective(NerAutoLabelResultPO po);
}
