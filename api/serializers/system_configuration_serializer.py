import json

from api.models.system_configuration import CompanyEmail, DataStatus, DataSubStatus, DataSource, DataChannel, \
    EmailSyntax, EmailTemplate, CompanyLogo
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEmail
        fields = ['id', 'email', 'company', 'created_at']


class CreateCompanyEmailRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=1024, required=True)
    password = serializers.CharField(max_length=1024, required=False, allow_null=True)
    company_id = serializers.IntegerField(required=True)


class CreateCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class GetCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class UpdateCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='CompanyEmail id', required=True)
    email = serializers.CharField(max_length=1024, required=False)
    password = serializers.CharField(max_length=1024, required=False, allow_null=True)


class UpdateCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class FilterCompanyEmailRequestParamSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=1024, required=False, allow_blank=True, allow_null=True)


class FilterCompanyEmailRequestSerializer(BasePagingSerializer):
    filter = FilterCompanyEmailRequestParamSerializer()


class FilterCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CompanyEmailSerializer())


class DeleteCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='CompanyEmail id')


class DeleteCompanyEmailResponseSerializer(BaseResponseSerializer):
    pass


class DataSubStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSubStatus
        fields = ['id', 'name', 'data_status', 'company', 'index', 'color', 'created_at', 'choose_by_default']


class DataStatusSerializer(serializers.ModelSerializer):
    data_sub_status = DataSubStatusSerializer(many=True)
    class Meta:
        model = DataStatus
        fields = ['id', 'name', 'company', 'index', 'color', 'created_at', 'choose_by_default', 'data_sub_status']


class CreateDataStatusRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=True)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreateDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class GetDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class UpdateDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataStatus id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=True)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdateDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class FilterDataStatusRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterDataStatusRequestSerializer(BasePagingSerializer):
    filter = FilterDataStatusRequestParamSerializer()


class FilterDataStatusResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataStatusSerializer())


class DeleteDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataStatus id')


class DeleteDataStatusResponseSerializer(BaseResponseSerializer):
    pass


class CreateDataSubStatusRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    data_status_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreateDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = DataSubStatusSerializer()


class GetDataSubStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = DataSubStatusSerializer()


class UpdateDataSubStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSubStatus id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdateDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = DataSubStatusSerializer()


class FilterDataSubStatusRequestParamSerializer(serializers.Serializer):
    data_status_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterDataSubStatusRequestSerializer(BasePagingSerializer):
    filter = FilterDataSubStatusRequestParamSerializer()


class FilterDataSubStatusResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataSubStatusSerializer())


class DeleteDataSubStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSubStatus id')


class DeleteDataSubStatusResponseSerializer(BaseResponseSerializer):
    pass


class DataChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataChannel
        fields = ['id', 'name', 'data_source', 'company', 'created_at', 'choose_by_default']


class DataSourceSerializer(serializers.ModelSerializer):
    data_channels = DataChannelSerializer(many=True)
    class Meta:
        model = DataSource
        fields = ['id', 'name', 'company', 'created_at', 'choose_by_default', 'data_channels']


class CreateDataSourceRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreateDataSourceResponseSerializer(BaseResponseSerializer):
    data = DataSourceSerializer()


class GetDataSourceRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataSourceResponseSerializer(BaseResponseSerializer):
    data = DataSourceSerializer()


class UpdateDataSourceRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSource id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdateDataSourceResponseSerializer(BaseResponseSerializer):
    data = DataSourceSerializer()


class FilterDataSourceRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterDataSourceRequestSerializer(BasePagingSerializer):
    filter = FilterDataSourceRequestParamSerializer()


class FilterDataSourceResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataSourceSerializer())


class DeleteDataSourceRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataSource id')


class DeleteDataSourceResponseSerializer(BaseResponseSerializer):
    pass


class CreateDataChannelRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    data_source_id = serializers.IntegerField(required=True)
    company_id = serializers.IntegerField(required=True)


class CreateDataChannelResponseSerializer(BaseResponseSerializer):
    data = DataChannelSerializer()


class GetDataChannelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataChannelResponseSerializer(BaseResponseSerializer):
    data = DataChannelSerializer()


class UpdateDataChannelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataChannel id', required=True)
    name = serializers.CharField(max_length=1024, required=False)


class UpdateDataChannelResponseSerializer(BaseResponseSerializer):
    data = DataChannelSerializer()


class FilterDataChannelRequestParamSerializer(serializers.Serializer):
    data_source_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterDataChannelRequestSerializer(BasePagingSerializer):
    filter = FilterDataChannelRequestParamSerializer()


class FilterDataChannelResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataChannelSerializer())


class DeleteDataChannelRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataChannel id')


class DeleteDataChannelResponseSerializer(BaseResponseSerializer):
    pass


class EmailSyntaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSyntax
        fields = ['id', 'code', 'column_name', 'description', 'company', 'created_at']


class CreateEmailSyntaxRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=True)
    column_name = serializers.CharField(max_length=256, required=False, allow_null=True)
    company_id = serializers.IntegerField(required=True)


class CreateEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = EmailSyntaxSerializer()


class GetEmailSyntaxRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = EmailSyntaxSerializer()


class UpdateEmailSyntaxRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=256, required=False, allow_null=True)
    column_name = serializers.CharField(max_length=256, required=False, allow_null=True)


class UpdateEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = EmailSyntaxSerializer()


class FilterEmailSyntaxRequestParamSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=False)
    column_name = serializers.CharField(max_length=256, required=False)


class FilterEmailSyntaxRequestSerializer(BasePagingSerializer):
    filter = FilterEmailSyntaxRequestParamSerializer()


class FilterEmailSyntaxResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=EmailSyntaxSerializer())


class DeleteEmailSyntaxRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='EmailSyntax id')


class DeleteEmailSyntaxResponseSerializer(BaseResponseSerializer):
    pass


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'code', 'email_name', 'content', 'company', 'created_at']


class CreateEmailTemplateRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=True)
    email_name = serializers.CharField()
    content = serializers.CharField()
    company_id = serializers.IntegerField(required=True)


class CreateEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = EmailTemplateSerializer()


class GetEmailTemplateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = EmailTemplateSerializer()


class UpdateEmailTemplateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=256, required=False, allow_null=True)
    email_name = serializers.CharField(required=False, allow_null=True)
    content = serializers.CharField(required=False, allow_null=True)


class UpdateEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = EmailTemplateSerializer()


class FilterEmailTemplateRequestParamSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=256, required=False)
    email_name = serializers.CharField(max_length=256, required=False)


class FilterEmailTemplateRequestSerializer(BasePagingSerializer):
    filter = FilterEmailTemplateRequestParamSerializer()


class FilterEmailTemplateResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=EmailTemplateSerializer())


class DeleteEmailTemplateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='EmailTemplate id')


class DeleteEmailTemplateResponseSerializer(BaseResponseSerializer):
    pass


class CompanyLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyLogo
        fields = ['id', 'logo', 'company', 'created_at']


class CreateCompanyLogoRequestSerializer(serializers.Serializer):
    logo = serializers.FileField()
    company_id = serializers.IntegerField(required=True)


class CreateCompanyLogoResponseSerializer(BaseResponseSerializer):
    data = CompanyLogoSerializer()


class GetCompanyLogoRequestSerializer(serializers.Serializer):
    pass


class GetCompanyLogoResponseSerializer(BaseResponseSerializer):
    data = CompanyLogoSerializer()


class UpdateCompanyLogoRequestSerializer(serializers.Serializer):
    logo = serializers.FileField()


class UpdateCompanyLogoResponseSerializer(BaseResponseSerializer):
    data = CompanyLogoSerializer()


class DeleteCompanyLogoRequestSerializer(serializers.Serializer):
    pass


class DeleteCompanyLogoResponseSerializer(BaseResponseSerializer):
    pass