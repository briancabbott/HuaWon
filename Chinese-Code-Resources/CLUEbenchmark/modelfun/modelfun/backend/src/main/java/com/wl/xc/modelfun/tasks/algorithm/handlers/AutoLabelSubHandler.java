package com.wl.xc.modelfun.tasks.algorithm.handlers;

import com.wl.xc.modelfun.commons.enums.AlgorithmTaskType;
import com.wl.xc.modelfun.commons.exceptions.BusinessException;
import com.wl.xc.modelfun.commons.exceptions.BusinessIllegalStateException;
import com.wl.xc.modelfun.entities.po.IntegrationRecordsPO;
import com.wl.xc.modelfun.tasks.algorithm.AlgorithmTask;
import java.time.LocalDateTime;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * @version 1.0
 * @date 2022/4/20 11:45
 */
@Slf4j
@Component
public class AutoLabelSubHandler extends AutoLabelHandler {

  @Override
  public AlgorithmTaskType getType() {
    return AlgorithmTaskType.NULL;
  }

  @Override
  protected void handleOnError(AlgorithmTask task, Exception exception) {
    Long recordId = task.getRecordId();
    IntegrationRecordsPO integrationRecordsPO = new IntegrationRecordsPO();
    integrationRecordsPO.setId(recordId);
    integrationRecordsPO.setLabeled(3);
    integrationRecordsPO.setUpdateDatetime(LocalDateTime.now());
    integrationRecordsService.updateById(integrationRecordsPO);
    if (exception instanceof BusinessException) {
      throw new BusinessIllegalStateException(String.format("自动标注失败，错误信息：%s", exception.getMessage()));
    } else {
      throw new BusinessIllegalStateException(String.format("自动标注失败，错误信息：%s！", "系统内部错误，请联系管理员"));
    }
  }
}
